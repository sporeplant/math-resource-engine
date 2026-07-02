using System.IO;
using System.Reflection;

var enDir = @"C:\Program Files (x86)\Seewo\EasiNote5\EasiNote5_5.2.4.9801";
var mainDir = Path.Combine(enDir, "Main");
var runtimeDlls = Directory.GetFiles(Path.Combine(enDir, "runtime"), "*.dll", SearchOption.AllDirectories);
var mainDlls = Directory.GetFiles(mainDir, "*.dll");
var resolver = new PathAssemblyResolver(mainDlls.Concat(runtimeDlls));
using var mlc = new MetadataLoadContext(resolver);

foreach (var dll in mainDlls.OrderBy(Path.GetFileName))
{
    try
    {
        var asm = mlc.LoadFromAssemblyPath(dll);
        var hits = asm.GetTypes().Where(t =>
            t.FullName?.Contains("Cvte.Paint.Features.Elements.Texts.TextElement", StringComparison.OrdinalIgnoreCase) == true ||
            t.FullName?.Contains("RichTextSaveInfo", StringComparison.OrdinalIgnoreCase) == true ||
            t.FullName?.Contains("TextSaveInfo", StringComparison.OrdinalIgnoreCase) == true).ToList();
        if (hits.Count == 0) continue;
        Console.WriteLine($"===== {Path.GetFileName(dll)} =====");
        foreach (var t in hits)
        {
            Console.WriteLine($"TYPE {t.FullName} public={t.IsPublic}");
            foreach (var c in t.GetConstructors(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance))
            {
                var pars = string.Join(", ", c.GetParameters().Select(p => $"{p.ParameterType.FullName} {p.Name}"));
                Console.WriteLine($"  CTOR {t.Name}({pars}) public={c.IsPublic}");
            }
            foreach (var p in t.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance).OrderBy(p => p.Name))
            {
                Console.WriteLine($"  PROP {(p.GetMethod?.IsStatic == true ? "static " : "")}{p.PropertyType.FullName} {p.Name} publicGet={p.GetMethod?.IsPublic} publicSet={p.SetMethod?.IsPublic}");
            }
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance).Where(m => !m.IsSpecialName).OrderBy(m => m.Name))
            {
                var pars = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.FullName} {p.Name}"));
                Console.WriteLine($"  METH {(m.IsStatic ? "static " : "")}{m.ReturnType.FullName} {m.Name}({pars}) public={m.IsPublic}");
            }
        }
    }
    catch { }
}
