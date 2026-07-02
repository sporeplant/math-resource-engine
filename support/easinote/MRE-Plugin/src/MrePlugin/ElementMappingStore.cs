using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace MrePlugin;

/// <summary>
/// MRE 元素 ID 与 EasiNote 元素 ID 的映射存储。
/// 用于后续增量更新时定位元素，避免重复创建。
///
/// 映射持久化到课件目录下的 .mre-mapping.json 文件。
/// </summary>
public static class ElementMappingStore
{
    private static readonly Dictionary<string, string> _map = new();
    private static string? _mappingFilePath;

    /// <summary>
    /// 建立 MRE 元素 ID → EasiNote 元素 ID 的映射。
    /// </summary>
    /// <param name="mreElementId">MRE lesson.json 中的元素 id。</param>
    /// <param name="enElementId">EasiNote 中元素的唯一标识。</param>
    public static void Set(string mreElementId, string enElementId)
    {
        _map[mreElementId] = enElementId;
    }

    /// <summary>
    /// 通过 MRE 元素 ID 查找对应的 EasiNote 元素 ID。
    /// </summary>
    /// <returns>如果找不到则返回 null。</returns>
    public static string? Get(string mreElementId)
    {
        return _map.TryGetValue(mreElementId, out var value) ? value : null;
    }

    /// <summary>
    /// 设置映射文件的保存路径。
    /// </summary>
    public static void SetMappingFile(string path)
    {
        _mappingFilePath = path;

        // 如果文件已存在，加载已有映射
        if (File.Exists(path))
        {
            try
            {
                var json = File.ReadAllText(path);
                var loaded = JsonSerializer.Deserialize<Dictionary<string, string>>(json);
                if (loaded is not null)
                {
                    foreach (var kv in loaded)
                    {
                        _map[kv.Key] = kv.Value;
                    }
                }
            }
            catch
            {
                // 加载失败时忽略，后续保存会覆盖
            }
        }
    }

    /// <summary>
    /// 将当前映射持久化到文件。
    /// </summary>
    public static void Save()
    {
        if (_mappingFilePath is null) return;

        try
        {
            var json = JsonSerializer.Serialize(_map, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(_mappingFilePath, json);
        }
        catch
        {
            // 保存失败不阻塞导入流程
        }
    }

    /// <summary>
    /// 检查某个 MRE 元素 ID 是否已经存在映射（即已创建过）。
    /// </summary>
    public static bool HasMapping(string mreElementId)
    {
        return _map.ContainsKey(mreElementId);
    }

    /// <summary>
    /// 清空所有映射。
    /// </summary>
    public static void Clear()
    {
        _map.Clear();
    }

    /// <summary>
    /// 当前映射数量。
    /// </summary>
    public static int Count => _map.Count;
}
