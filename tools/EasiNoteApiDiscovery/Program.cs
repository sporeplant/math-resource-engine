using System.IO;
using System.Reflection;

var enDir = @"C:\Program Files (x86)\Seewo\EasiNote5\EasiNote5_5.2.4.9801";
var mainDir = Path.Combine(enDir, "Main");

var resolver = new PathAssemblyResolver(
    Directory.GetFiles(mainDir, "*.dll")
        .Concat(Directory.GetFiles(Path.Combine(enDir, "runtime", "shared", "Microsoft.WindowsDesktop.App"), "*.dll", SearchOption.AllDirectories))
        .Concat(Directory.GetFiles(Path.Combine(enDir, "runtime", "shared", "Microsoft.NETCore.App"), "*.dll", SearchOption.AllDirectories))
);
using var mlc = new System.Reflection.MetadataLoadContext(resolver);

// Search all assemblies for Element, ImageElement, and TextEditor
foreach (var dllPath in Directory.GetFiles(mainDir, "*.dll"))
{
    try
    {
        var asm = mlc.LoadFromAssemblyPath(dllPath);
        var name = Path.GetFileName(dllPath);
        bool found = false;

        foreach (var t in asm.GetExportedTypes())
        {
            // Element base class
            if (t.Name == "Element" && t.IsPublic && t.IsAbstract && t.FullName != null && t.FullName.Contains("Paint"))
            {
                Console.WriteLine($"## [{name}] Element: {t.FullName}");
                Console.WriteLine($"  BaseType: {t.BaseType?.FullName}");
                Console.WriteLine("  --- Properties ---");
                foreach (var p in t.GetProperties().Where(p => p.DeclaringType == t))
                {
                    var gs = (p.CanRead ? "get" : "") + (p.CanWrite ? ";set" : "");
                    Console.WriteLine($"  {Fmt(p.PropertyType)} {p.Name} {{{gs}}}");
                }
                Console.WriteLine();
                found = true;
            }

            // ImageElement
            if (t.Name == "ImageElement" && !t.IsAbstract)
            {
                Console.WriteLine($"## [{name}] ImageElement: {t.FullName}");
                Console.WriteLine($"  BaseType: {t.BaseType?.FullName}");
                foreach (var c in t.GetConstructors().Where(c => c.IsPublic))
                {
                    var pars = string.Join(", ", c.GetParameters().Select(p => $"{Fmt(p.ParameterType)} {p.Name}"));
                    Console.WriteLine($"  ctor({pars})");
                }
                foreach (var p in t.GetProperties().Where(p => p.DeclaringType == t).Take(30))
                {
                    var gs = (p.CanRead ? "get" : "") + (p.CanWrite ? ";set" : "");
                    Console.WriteLine($"  {Fmt(p.PropertyType)} {p.Name} {{{gs}}}");
                }
                Console.WriteLine();
                found = true;
            }

            // RichTextSaveInfo (used by SetRichText)
            if (t.Name == "RichTextSaveInfo" && t.IsPublic)
            {
                Console.WriteLine($"## [{name}] RichTextSaveInfo: {t.FullName}");
                foreach (var c in t.GetConstructors().Where(c => c.IsPublic))
                {
                    var pars = string.Join(", ", c.GetParameters().Select(p => $"{Fmt(p.ParameterType)} {p.Name}"));
                    Console.WriteLine($"  ctor({pars})");
                }
                foreach (var p in t.GetProperties().Where(p => p.DeclaringType == t).Take(15))
                {
                    var gs = (p.CanRead ? "get" : "") + (p.CanWrite ? ";set" : "");
                    Console.WriteLine($"  {Fmt(p.PropertyType)} {p.Name} {{{gs}}}");
                }
                Console.WriteLine();
                found = true;
            }

            // PictureElement (might be image)
            if (t.Name == "PictureElement" && !t.IsAbstract)
            {
                Console.WriteLine($"## [{name}] PictureElement: {t.FullName}");
                foreach (var c in t.GetConstructors().Where(c => c.IsPublic))
                {
                    var pars = string.Join(", ", c.GetParameters().Select(p => $"{Fmt(p.ParameterType)} {p.Name}"));
                    Console.WriteLine($"  ctor({pars})");
                }
                foreach (var p in t.GetProperties().Where(p => p.DeclaringType == t).Take(20))
                {
                    var gs = (p.CanRead ? "get" : "") + (p.CanWrite ? ";set" : "");
                    Console.WriteLine($"  {Fmt(p.PropertyType)} {p.Name} {{{gs}}}");
                }
                Console.WriteLine();
                found = true;
            }
        }

        if (found) Console.WriteLine("---");
    }
    catch { }
}

// Also search for Element base in loaded types more broadly
foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
{
    foreach (var t in asm.GetTypes())
    {
        if (t.Name == "Element" && t.IsPublic && t.IsAbstract)
        {
            Console.WriteLine($"[runtime] Element: {t.FullName} from {asm.GetName().Name}");
        }
    }
}

static string Fmt(Type t)
{
    if (t == typeof(void)) return "void";
    if (t.IsGenericType)
    {
        var name = t.Name[..t.Name.IndexOf('`')];
        var args = string.Join(", ", t.GenericTypeArguments.Select(Fmt));
        return $"{name}<{args}>";
    }
    return t.Name;
}
