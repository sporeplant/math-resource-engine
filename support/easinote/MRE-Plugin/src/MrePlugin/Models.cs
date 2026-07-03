using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace MrePlugin;

/// <summary>
/// MRE lesson.json 顶层文档结构。
///
/// 示例：
/// {
///   "slides": [
///     {
///       "id": "slide_01",
///       "elements": [
///         {
///           "id": "el_01",
///           "type": "text",
///           "text": "21.1 一元二次方程",
///           "x": 100, "y": 50,
///           "width": 800, "height": 60,
///           "fontSize": 28, "bold": true
///         }
///       ]
///     }
///   ]
/// }
/// </summary>
public class LessonDocument
{
    [JsonPropertyName("slides")]
    public List<SlideData>? Slides { get; set; }
}

/// <summary>
/// 单个页面（Slide）的数据。
/// </summary>
public class SlideData
{
    /// <summary>MRE 内部页面 ID，用于后续增量同步。</summary>
    [JsonPropertyName("id")]
    public string? Id { get; set; }

    /// <summary>页面中的所有元素。</summary>
    [JsonPropertyName("elements")]
    public List<ElementData>? Elements { get; set; }

    /// <summary>页面背景颜色（可选）。</summary>
    [JsonPropertyName("background")]
    public string? Background { get; set; }
}

/// <summary>
/// 单个元素的数据。根据 type 字段区分不同类型。
/// </summary>
public class ElementData
{
    /// <summary>MRE 内部元素 ID，用于增量同步时定位元素。</summary>
    [JsonPropertyName("id")]
    public string? Id { get; set; }

    /// <summary>
    /// 元素类型：
    /// - "text"    : 文本框
    /// - "image"   : 图片
    /// - "formula" : 公式图片（实际存储为图片，此处标记类型差异）
    /// - "shape"   : 形状（矩形、圆形等）
    /// </summary>
    [JsonPropertyName("type")]
    public string? Type { get; set; }

    // ── 通用属性 ──

    /// <summary>左上角 X 坐标（页面坐标系，像素）。</summary>
    [JsonPropertyName("x")]
    public double? X { get; set; }

    /// <summary>左上角 Y 坐标（页面坐标系，像素）。</summary>
    [JsonPropertyName("y")]
    public double? Y { get; set; }

    /// <summary>元素宽度（像素）。</summary>
    [JsonPropertyName("width")]
    public double? Width { get; set; }

    /// <summary>元素高度（像素）。</summary>
    [JsonPropertyName("height")]
    public double? Height { get; set; }

    // ── 文本元素属性 ──

    /// <summary>文本内容（type=text 时使用）。</summary>
    [JsonPropertyName("text")]
    public string? Text { get; set; }

    /// <summary>字体大小（pt）。</summary>
    [JsonPropertyName("fontSize")]
    public double? FontSize { get; set; }

    /// <summary>是否加粗。</summary>
    [JsonPropertyName("bold")]
    public bool? Bold { get; set; }

    /// <summary>是否斜体。</summary>
    [JsonPropertyName("italic")]
    public bool? Italic { get; set; }

    /// <summary>字体族名称（如 "方正小标宋简体"、"Times New Roman"）。</summary>
    [JsonPropertyName("fontFamily")]
    public string? FontFamily { get; set; }

    /// <summary>字体颜色（HTML 颜色格式，如 "#333333"）。</summary>
    [JsonPropertyName("color")]
    public string? Color { get; set; }

    /// <summary>文本对齐：left/center/right。</summary>
    [JsonPropertyName("align")]
    public string? Align { get; set; }

    // ── 图片元素属性 ──

    /// <summary>图片资源路径（相对于 assets 目录，type=image/formula 时使用）。</summary>
    [JsonPropertyName("src")]
    public string? Src { get; set; }

    // ── 形状元素属性 ──

    /// <summary>形状类型：rectangle/ellipse/line（type=shape 时使用）。</summary>
    [JsonPropertyName("shapeType")]
    public string? ShapeType { get; set; }

    /// <summary>填充颜色。</summary>
    [JsonPropertyName("fill")]
    public string? Fill { get; set; }

    /// <summary>边框颜色。</summary>
    [JsonPropertyName("stroke")]
    public string? Stroke { get; set; }

    /// <summary>边框宽度。</summary>
    [JsonPropertyName("strokeWidth")]
    public double? StrokeWidth { get; set; }
}
