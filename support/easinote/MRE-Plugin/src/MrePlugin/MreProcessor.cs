using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;

using Cvte.EasiNote;
using Cvte.Paint.Framework;
using Cvte.Paint.Features.Elements;
using Cvte.Paint.Features.Elements.Texts;
using Cvte.Paint.Features.Elements.Shapes;
using Cvte.Windows.TextEditorPlus.Storage;

namespace MrePlugin;

/// <summary>
/// MRE lesson.json 处理结果。
/// </summary>
public readonly struct MreProcessResult
{
    public bool Success { get; init; }
    public int SlideCount { get; init; }
    public int ElementCount { get; init; }
    public string? ErrorMessage { get; init; }

    public static MreProcessResult Ok(int slides, int elements) =>
        new() { Success = true, SlideCount = slides, ElementCount = elements };

    public static MreProcessResult Fail(string msg) =>
        new() { Success = false, ErrorMessage = msg };
}

/// <summary>
/// MRE lesson.json → 希沃白板课件转换处理器。
///
/// 已验证的 EasiNote API（来源：EasiNote5_5.2.4.9801 反射）：
///   - Slide: new Slide() / new Slide(string id)
///   - Slide.Add(Element) / Slide.Add(IEnumerable&lt;Element&gt;)
///   - Board.Insert(Slide) / Board.InsertAt(Slide, int)
///   - TextElement: new TextElement() / new TextElement(bool isEditable)
///   - TextElement.TextEditor.SetRichText(RichTextSaveInfo, bool)
///   - RichTextSaveInfo: Text, Paragraphs, SizeToContent
///   - ShapeElement: new ShapeElement(ShapeType)
///   - ShapeType: 枚举（Rectangle, Ellipse, Line 等）
/// </summary>
public static class MreProcessor
{
    /// <summary>
    /// 处理 lesson.json，在当前课件中创建对应页面和元素。
    /// </summary>
    public static async Task<MreProcessResult> ProcessLessonJsonAsync(string filePath)
    {
        // 1. 读取并解析 JSON
        string jsonContent;
        try { jsonContent = await File.ReadAllTextAsync(filePath); }
        catch (Exception ex) { return MreProcessResult.Fail($"无法读取文件：{ex.Message}"); }

        LessonDocument? lesson;
        try
        {
            lesson = JsonSerializer.Deserialize<LessonDocument>(jsonContent,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
        }
        catch (JsonException ex) { return MreProcessResult.Fail($"JSON 解析失败：{ex.Message}"); }

        if (lesson?.Slides is null || lesson.Slides.Count == 0)
            return MreProcessResult.Fail("lesson.json 中没有 slides 或为空。");

        // 2. 获取 Board（画板）和 asset 基础路径
        var board = GetBoard();
        if (board is null)
            return MreProcessResult.Fail("无法获取 Board 对象。可能是未处于备课模式。");

        var assetBaseDir = Path.GetDirectoryName(filePath) ?? "";
        var assetsDir = Path.Combine(assetBaseDir, "assets");

        int totalElements = 0;
        for (int i = 0; i < lesson.Slides.Count; i++)
        {
            var slideData = lesson.Slides[i];
            if (slideData.Elements is null) continue;

            try
            {
                // 创建 Slide 并插入到 Board
                var slide = new Slide(slideData.Id ?? $"mre_{i}");
                slide.Background = ParseBrush(slideData.Background);
                board.Insert(slide);
                // board.Insert(slide);  — 追加到末尾

                // 在新页面上逐个创建元素
                foreach (var elemData in slideData.Elements)
                {
                    try
                    {
                        CreateElement(slide, elemData, assetsDir);
                        totalElements++;
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine(
                            $"[MRE] 元素创建失败: id={elemData.Id}, type={elemData.Type}, error={ex.Message}");
                    }
                }
            }
            catch (Exception ex)
            {
                return MreProcessResult.Fail($"处理第 {i + 1} 个页面时出错：{ex.Message}");
            }
        }

        return MreProcessResult.Ok(lesson.Slides.Count, totalElements);
    }

    // ═══════════════════════════════════════════════════
    // 元素创建
    // ═══════════════════════════════════════════════════

    private static void CreateElement(Slide slide, ElementData data, string assetsDir)
    {
        switch (data.Type?.ToLowerInvariant())
        {
            case "text":
                CreateTextElement(slide, data);
                break;
            case "image":
            case "formula":
                CreateImageElement(slide, data, assetsDir);
                break;
            case "shape":
                CreateShapeElement(slide, data);
                break;
        }
    }

    /// <summary>
    /// 创建文本框元素。
    /// 已验证 API: TextElement(bool isEditable), TextEditor.SetRichText(RichTextSaveInfo, bool)
    /// </summary>
    private static void CreateTextElement(Slide slide, ElementData data)
    {
        var textElement = new TextElement(isEditable: false);

        // 位置和大小
        double x = data.X.GetValueOrDefault(100);
        double y = data.Y.GetValueOrDefault(50);
        double w = data.Width.GetValueOrDefault(800);
        double h = data.Height.GetValueOrDefault(60);
        textElement.Bounds = new Rect(x, y, w, h);

        // 文本内容
        var richText = new RichTextSaveInfo
        {
            Text = data.Text ?? "",
            SizeToContent = SizeToContent.WidthAndHeight,
        };
        textElement.TextEditor.SetRichText(richText, withForceRedraw: false);

        // 字体样式 — 通过 ParagraphSaveInfo 设置
        if (data.FontSize.HasValue || data.Bold == true || data.Italic == true || !string.IsNullOrEmpty(data.Color))
        {
            var paragraph = richText.Paragraphs?.FirstOrDefault();
            if (paragraph is not null)
            {
                // paragraph.FontSize / paragraph.Bold / etc.
                // 具体属性名需在 EasiNote 运行时通过 TextEditor API 验证
            }
        }

        slide.Add(textElement);
    }

    /// <summary>
    /// 创建图片元素。
    /// 注意: ImageElement 在当前公开 API 中不可见（可能为 internal）。
    /// 备选: 使用 InsertMedia API 或通过反射创建。
    /// </summary>
    private static void CreateImageElement(Slide slide, ElementData data, string assetsDir)
    {
        if (string.IsNullOrEmpty(data.Src)) return;

        var imagePath = Path.Combine(assetsDir, data.Src);
        if (!File.Exists(imagePath))
        {
            System.Diagnostics.Debug.WriteLine($"[MRE] 图片文件不存在: {imagePath}");
            return;
        }

        // ⚠️ ImageElement 是 internal 类型，需通过以下方式之一创建：
        //
        // 方案 A（推荐）: 使用 BoardService.AddResource + InsertMedia
        //   var resourcePath = boardService.AddResource(imagePath);
        //   然后通过 InsertElementByJson 或 InsertMedia 插入
        //
        // 方案 B: 通过反射创建 ImageElement
        //   var imageType = typeof(TextElement).Assembly.GetType("Cvte.Paint.Features.Elements.Images.ImageElement");
        //   var imageElement = Activator.CreateInstance(imageType);
        //
        // 方案 C: 使用 Element 工厂方法
        //   查找 Element 的静态 Create 方法

        System.Diagnostics.Debug.WriteLine($"[MRE] ImageElement 创建待实现: src={data.Src}");
    }

    /// <summary>
    /// 创建形状元素。
    /// 已验证 API: ShapeElement(ShapeType)
    /// </summary>
    private static void CreateShapeElement(Slide slide, ElementData data)
    {
        var shapeType = ParseShapeType(data.ShapeType);
        var shapeElement = new ShapeElement(shapeType);

        double x = data.X.GetValueOrDefault(100);
        double y = data.Y.GetValueOrDefault(100);
        double w = data.Width.GetValueOrDefault(200);
        double h = data.Height.GetValueOrDefault(100);
        shapeElement.Bounds = new Rect(x, y, w, h);

        // 填充和边框（具体属性名需运行时验证）
        // if (!string.IsNullOrEmpty(data.Fill)) shapeElement.Fill = ParseBrush(data.Fill);
        // if (!string.IsNullOrEmpty(data.Stroke)) shapeElement.Stroke = ParseBrush(data.Stroke);

        slide.Add(shapeElement);
    }

    // ═══════════════════════════════════════════════════
    // 辅助方法
    // ═══════════════════════════════════════════════════

    /// <summary>
    /// 获取当前 Board（画板）对象。
    /// Board 是 Slide 的容器，负责页面的增删和导航。
    /// 通过 EN.EditingBoardApi.Board 获取。
    /// </summary>
    private static Board? GetBoard()
    {
        try
        {
            // Board 通过 EditingBoardApi 暴露
            var boardProperty = typeof(EN).Assembly
                .GetType("Cvte.EasiNote.EditingBoardApi")?
                .GetProperty("Board");
            if (boardProperty is null) return null;

            // EditingBoardApi 的获取方式取决于 EN 框架版本
            // EN.EditingBoardApi 是公共属性
            return boardProperty.GetValue(null) as Board;
        }
        catch
        {
            return null;
        }
    }

    private static ShapeType ParseShapeType(string? type)
    {
        return type?.ToLowerInvariant() switch
        {
            "rectangle" => ShapeType.Rectangle,
            "ellipse" => ShapeType.Ellipse,
            "circle" => ShapeType.Ellipse,
            "line" => ShapeType.Line,
            "triangle" => ShapeType.Triangle,
            _ => ShapeType.Rectangle,
        };
    }

    private static Brush? ParseBrush(string? color)
    {
        if (string.IsNullOrEmpty(color)) return null;
        try
        {
            return (Brush)new System.Windows.Media.BrushConverter().ConvertFromString(color)!;
        }
        catch
        {
            return null;
        }
    }
}
