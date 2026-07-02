namespace MrePlugin;

/// <summary>
/// MRE 插件事件 ID，用于希沃后台数据分析。
/// </summary>
public static class EventId
{
    /// <summary>用户点击"MRE导入"按钮。</summary>
    public const string MreImportClicked = "MrePlugin.Import.Clicked";

    /// <summary>lesson.json 解析成功。</summary>
    public const string MreParseSuccess = "MrePlugin.Parse.Success";

    /// <summary>lesson.json 解析失败。</summary>
    public const string MreParseFailed = "MrePlugin.Parse.Failed";

    /// <summary>页面创建完成。</summary>
    public const string MreSlideCreated = "MrePlugin.Slide.Created";

    /// <summary>元素创建完成。</summary>
    public const string MreElementCreated = "MrePlugin.Element.Created";

    /// <summary>导入流程完成。</summary>
    public const string MreImportCompleted = "MrePlugin.Import.Completed";

    /// <summary>导入流程失败。</summary>
    public const string MreImportFailed = "MrePlugin.Import.Failed";
}
