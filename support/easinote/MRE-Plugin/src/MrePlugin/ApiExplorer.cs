using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace MrePlugin;

/// <summary>
/// EasiNote API 探索器。
/// 用于在 EasiNote 环境中运行时，通过反射发现页面创建和元素创建相关 API。
///
/// 输出结果写入 %TEMP%\\MrePlugin_ApiDiscovery.txt，供开发者查阅。
/// </summary>
public static class ApiExplorer
{
    private static readonly string LogPath =
        Path.Combine(Path.GetTempPath(), "MrePlugin_ApiDiscovery.txt");

    /// <summary>
    /// 探索 EditingBoardApi 的类型和方法，输出到日志文件。
    /// 在插件初始化时调用一次即可。
    /// </summary>
    public static void ExploreEditingBoardApi()
    {
        try
        {
            var sb = new StringBuilder();
            sb.AppendLine($"=== MRE API Discovery === {DateTime.Now}");
            sb.AppendLine();

            // 1. 探索 EN.EditingBoardApi 的类型
            var boardApiType = typeof(Cvte.EasiNote.EN).Assembly
                .GetType("Cvte.EasiNote.EditingBoardApi");
            if (boardApiType is not null)
            {
                sb.AppendLine("## EditingBoardApi");
                sb.AppendLine($"  Type: {boardApiType.FullName}");
                ExploreType(boardApiType, sb);
            }

            // 2. 探索 Slide 类型
            var slideType = typeof(Cvte.Paint.Framework.Slide);
            sb.AppendLine();
            sb.AppendLine("## Slide");
            sb.AppendLine($"  Type: {slideType.FullName}");
            ExploreType(slideType, sb);

            // 3. 探索 TextElement 类型
            var textElementType = typeof(Cvte.Paint.Features.Elements.Texts.TextElement);
            sb.AppendLine();
            sb.AppendLine("## TextElement");
            sb.AppendLine($"  Type: {textElementType.FullName}");
            ExploreType(textElementType, sb);

            // 4. 搜索 ImageElement（可能在多个命名空间下）
            ExploreElementType(sb, "ImageElement");
            ExploreElementType(sb, "ShapeElement");
            ExploreElementType(sb, "PictureElement");
            ExploreElementType(sb, "FormulaElement");

            File.WriteAllText(LogPath, sb.ToString());
        }
        catch (Exception ex)
        {
            File.WriteAllText(LogPath, $"API 探索失败：{ex}");
        }
    }

    /// <summary>
    /// 在加载的程序集中按名称搜索元素类型。
    /// </summary>
    private static void ExploreElementType(StringBuilder sb, string typeName)
    {
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            try
            {
                foreach (var type in asm.GetTypes())
                {
                    if (type.Name.Equals(typeName, StringComparison.OrdinalIgnoreCase))
                    {
                        sb.AppendLine();
                        sb.AppendLine($"## {typeName} found in {asm.GetName().Name}");
                        sb.AppendLine($"  FullName: {type.FullName}");
                        ExploreType(type, sb);
                        return; // 找到第一个就够
                    }
                }
            }
            catch
            {
                // 某些程序集可能无法加载所有类型
            }
        }
    }

    /// <summary>
    /// 输出类型的公共构造函数、属性和方法。
    /// </summary>
    private static void ExploreType(Type type, StringBuilder sb)
    {
        // 公共构造函数
        var ctors = type.GetConstructors(BindingFlags.Public | BindingFlags.Instance);
        if (ctors.Length > 0)
        {
            sb.AppendLine("  Constructors:");
            foreach (var ctor in ctors)
            {
                var parameters = string.Join(", ",
                    ctor.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                sb.AppendLine($"    {type.Name}({parameters})");
            }
        }

        // 公共属性（选取最相关的）
        var props = type.GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Where(p => p.DeclaringType == type || !type.IsAbstract)
            .Take(30);
        if (props.Any())
        {
            sb.AppendLine("  Properties:");
            foreach (var prop in props)
            {
                var getSet = (prop.CanRead ? "get" : "") +
                             (prop.CanWrite ? "; set" : "");
                sb.AppendLine($"    {prop.PropertyType.Name} {prop.Name} {{ {getSet} }}");
            }
        }

        // 关键方法（名称包含 Create/Add/Insert/Remove/New 的方法）
        var methods = type.GetMethods(BindingFlags.Public | BindingFlags.Instance)
            .Where(m => !m.IsSpecialName && m.DeclaringType == type)
            .Where(m => m.Name.Contains("Create") || m.Name.Contains("Add") ||
                        m.Name.Contains("Insert") || m.Name.Contains("Remove") ||
                        m.Name.Contains("New") || m.Name.Contains("Slide") ||
                        m.Name.Contains("Page"))
            .Take(20);
        if (methods.Any())
        {
            sb.AppendLine("  Key Methods:");
            foreach (var method in methods)
            {
                var parameters = string.Join(", ",
                    method.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                sb.AppendLine($"    {method.ReturnType.Name} {method.Name}({parameters})");
            }
        }
    }
}
