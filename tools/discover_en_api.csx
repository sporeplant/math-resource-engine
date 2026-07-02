using System.Reflection;

var enDir = args.Length > 0 ? args[0] :
    @"C:\Program Files (x86)\Seewo\EasiNote5\EasiNote5_5.2.4.9801";

var mainDir = Path.Combine(enDir, "Main");
var outputPath = args.Length > 1 ? args[1] :
    Path.Combine(Path.GetTempPath(), "MrePlugin_ApiDiscovery.txt");

using var writer = new StreamWriter(outputPath, false);
writer.WriteLine($"=== MRE API Discovery ===");
writer.WriteLine($"EN Directory: {mainDir}");
writer.WriteLine($"Time: {DateTime.Now}");
writer.WriteLine();

// =============== 1. 加载核心 DLL ===============
var targetDlls = new[]
{
    "Cvte.Paint.Framework.dll",
    "Cvte.Paint.Shell.dll",
    "Cvte.Paint.Table.dll",
    "Cvte.Core.dll",
    "EasiNote.Api.dll",
    "EasiNote.PublicApi.dll",
    "EasiNote.dll",
    "Cvte.EasiUI.dll",
    "Cvte.GurnetUI.dll",
    "Cvte.GurnetUI.EasiNote.dll",
    "Cvte.Paint.Remark.dll",
    "EasiNote.Business.dll",
    "EasiNote.Global.dll",
    "Cvte.Paint.Chart.dll",
};

foreach (var dllName in targetDlls)
{
    var dllPath = Path.Combine(mainDir, dllName);
    if (!File.Exists(dllPath))
    {
        writer.WriteLine($"# {dllName} — NOT FOUND at {dllPath}");
        writer.WriteLine();
        continue;
    }

    try
    {
        var asm = Assembly.LoadFrom(dllPath);
        writer.WriteLine($"# {dllName}");
        writer.WriteLine($"  FullName: {asm.FullName}");
        writer.WriteLine($"  Location: {asm.Location}");
        writer.WriteLine();

        // 搜索关键类型
        var types = asm.GetExportedTypes();

        // ---- Slide 类型 ----
        foreach (var t in types.Where(t => t.Name == "Slide" || t.Name.EndsWith("Slide")))
        {
            DumpType(t, writer);
        }

        // ---- 带 "Element" 的类型 ----
        foreach (var t in types.Where(t =>
            t.Name.Contains("Element") &&
            t.IsPublic && !t.IsAbstract &&
            t.GetConstructors().Any(c => c.IsPublic && c.GetParameters().Length == 0)))
        {
            writer.WriteLine($"## public concrete Element: {t.FullName}");
            DumpConstructors(t, writer);
            DumpKeyProperties(t, writer, "Bounds", "Text", "Content", "Source",
                "Image", "FontSize", "FontWeight", "Foreground",
                "Id", "Uid", "Name", "Tag");
            writer.WriteLine();
        }

        // ---- 搜索 Create/Add Slide/Page 方法 ----
        foreach (var t in types.Where(t => t.Name.Contains("Board") || t.Name.Contains("Editing") ||
                                           t.Name.Contains("Api") || t.Name.Contains("Slide")))
        {
            var keyMethods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static)
                .Where(m => !m.IsSpecialName)
                .Where(m => m.Name.Contains("Create") || m.Name.Contains("Add") ||
                            m.Name.Contains("Insert") || m.Name.Contains("Remove") ||
                            m.Name.Contains("New") || m.Name.Contains("Slide") ||
                            m.Name.Contains("Page"))
                .Take(30)
                .ToList();

            if (keyMethods.Any())
            {
                writer.WriteLine($"## {t.FullName} — Key Methods:");
                foreach (var m in keyMethods)
                {
                    var pars = string.Join(", ", m.GetParameters().Select(p =>
                        $"{FormatType(p.ParameterType)} {p.Name}"));
                    writer.WriteLine($"  {FormatType(m.ReturnType)} {m.Name}({pars})");
                }
                writer.WriteLine();
            }
        }
    }
    catch (Exception ex)
    {
        writer.WriteLine($"# {dllName} — LOAD ERROR: {ex.GetType().Name}: {ex.Message}");
        writer.WriteLine();
    }
}

writer.WriteLine("=== DISCOVERY COMPLETE ===");
Console.WriteLine($"Discovery complete. Output: {outputPath}");

// =============== Helper Methods ===============

static void DumpType(Type t, StreamWriter w)
{
    w.WriteLine($"## {t.FullName}");
    w.WriteLine($"  IsPublic: {t.IsPublic}, IsAbstract: {t.IsAbstract}");
    if (t.BaseType is not null && t.BaseType != typeof(object))
        w.WriteLine($"  BaseType: {t.BaseType.FullName}");
    DumpConstructors(t, w);
    DumpKeyProperties(t, w, "Elements", "Bounds", "Id", "Name", "Index", "Background",
        "Width", "Height", "SlideIndex", "SlideId");
    DumpKeyMethods(t, w);
    w.WriteLine();
}

static void DumpConstructors(Type t, StreamWriter w)
{
    var ctors = t.GetConstructors(BindingFlags.Public | BindingFlags.Instance);
    if (ctors.Length == 0) return;
    w.WriteLine($"  Constructors ({ctors.Length}):");
    foreach (var c in ctors)
    {
        var pars = string.Join(", ", c.GetParameters().Select(p =>
            $"{FormatType(p.ParameterType)} {p.Name}"));
        w.WriteLine($"    {t.Name}({pars})");
    }
}

static void DumpKeyProperties(Type t, StreamWriter w, params string[] names)
{
    var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance);
    var matched = names
        .SelectMany(name => props.Where(p => p.Name.Equals(name, StringComparison.OrdinalIgnoreCase)))
        .Distinct()
        .ToList();

    if (matched.Count == 0) return;
    w.WriteLine($"  Key Properties:");
    foreach (var p in matched)
    {
        var gs = (p.CanRead ? "get" : "") + (p.CanWrite ? ";set" : "");
        w.WriteLine($"    {FormatType(p.PropertyType)} {p.Name} {{ {gs} }}");
    }
}

static void DumpKeyMethods(Type t, StreamWriter w)
{
    var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance)
        .Where(m => !m.IsSpecialName && m.DeclaringType == t)
        .Where(m => m.Name.Contains("Create") || m.Name.Contains("Add") ||
                    m.Name.Contains("Remove") || m.Name.Contains("Insert") ||
                    m.Name.Contains("Slide") || m.Name.Contains("Element") ||
                    m.Name.Contains("Page"))
        .Take(20).ToList();

    if (methods.Count == 0) return;
    w.WriteLine($"  Key Methods:");
    foreach (var m in methods)
    {
        var pars = string.Join(", ", m.GetParameters().Select(p =>
            $"{FormatType(p.ParameterType)} {p.Name}"));
        w.WriteLine($"    {FormatType(m.ReturnType)} {m.Name}({pars})");
    }
}

static string FormatType(Type t)
{
    if (t == typeof(void)) return "void";
    if (t.IsGenericType)
    {
        var name = t.Name[..t.Name.IndexOf('`')];
        var args = string.Join(", ", t.GenericTypeArguments.Select(FormatType));
        return $"{name}<{args}>";
    }
    return t.Name;
}
