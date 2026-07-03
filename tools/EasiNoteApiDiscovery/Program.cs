using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;

var enDir = @"C:\Program Files (x86)\Seewo\EasiNote5\EasiNote5_5.2.4.9801";
var dlls = Directory.GetFiles(enDir, "*.dll", SearchOption.AllDirectories)
    .Distinct(StringComparer.OrdinalIgnoreCase)
    .ToArray();

var resolver = new PathAssemblyResolver(dlls);
using var mlc = new MetadataLoadContext(resolver);

var targetDllNames = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
{
    "Cvte.Paint.Shell.dll",
    "EasiNote.UI.dll",
    "EasiNote.Api.dll",
    "Cvte.Storage.Standard.dll"
};

foreach (var dll in dlls.Where(path => targetDllNames.Contains(Path.GetFileName(path))).OrderBy(Path.GetFileName))
{
    Console.WriteLine($"===== {Path.GetFileName(dll)} =====");
    Assembly asm;
    try { asm = mlc.LoadFromAssemblyPath(dll); }
    catch (Exception ex)
    {
        Console.WriteLine($"LOAD FAIL {ex.Message}");
        continue;
    }

    foreach (var t in SafeGetTypes(asm).OrderBy(t => t.FullName))
    {
        var name = t.FullName ?? "";
        if (!ContainsAny(name, "Picture", "Image", "Media", "Multimedia", "InsertMedia", "InsertElement", "Uri")) continue;

        Console.WriteLine($"TYPE {name} public={t.IsPublic} abstract={t.IsAbstract} base={SafeTypeName(() => t.BaseType)}");

        foreach (var c in SafeGetConstructors(t))
            Console.WriteLine($"  CTOR public={c.IsPublic} {SafeParameters(c)}");

        foreach (var p in SafeGetProperties(t).Where(p => ContainsAny(p.Name, "Source", "Path", "Uri", "Url", "Picture", "Image", "Media", "Width", "Height", "X", "Y", "Bounds", "SaveInfo", "Resource", "File", "Data")).OrderBy(p => p.Name))
            Console.WriteLine($"  PROP {SafeTypeName(() => p.PropertyType)} {p.Name} getPublic={p.GetMethod?.IsPublic} setPublic={p.SetMethod?.IsPublic}");

        foreach (var m in SafeGetMethods(t).Where(m => !m.IsSpecialName && ContainsAny(m.Name, "SaveInfo", "Picture", "Image", "Media", "Source", "Create", "Insert", "Load", "Resource", "Open", "Init", "Uri")).OrderBy(m => m.Name))
            Console.WriteLine($"  METH public={m.IsPublic} static={m.IsStatic} {SafeTypeName(() => m.ReturnType)} {m.Name}({SafeParameters(m)})");
    }
}

static IEnumerable<Type> SafeGetTypes(Assembly asm)
{
    try { return asm.GetTypes(); }
    catch (ReflectionTypeLoadException ex) { return ex.Types.Where(t => t is not null)!; }
    catch { return Array.Empty<Type>(); }
}

static IEnumerable<ConstructorInfo> SafeGetConstructors(Type t)
{
    try { return t.GetConstructors(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance); }
    catch { return Array.Empty<ConstructorInfo>(); }
}

static IEnumerable<PropertyInfo> SafeGetProperties(Type t)
{
    try { return t.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static); }
    catch { return Array.Empty<PropertyInfo>(); }
}

static IEnumerable<MethodInfo> SafeGetMethods(Type t)
{
    try { return t.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static); }
    catch { return Array.Empty<MethodInfo>(); }
}

static string SafeParameters(MethodBase method)
{
    try { return string.Join(", ", method.GetParameters().Select(p => $"{SafeTypeName(() => p.ParameterType)} {p.Name}")); }
    catch { return "?"; }
}

static string SafeTypeName(Func<Type?> getType)
{
    try { return getType()?.FullName ?? ""; }
    catch { return "?"; }
}

static bool ContainsAny(string? value, params string[] needles)
{
    if (value is null) return false;
    return needles.Any(n => value.Contains(n, StringComparison.OrdinalIgnoreCase));
}
