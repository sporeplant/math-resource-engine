using System;
using System.Globalization;
using System.Threading.Tasks;
using Cvte.Composition;
using Cvte.EasiNote;
using dotnetCampus.EasiPlugins;

namespace MrePlugin;

/// <summary>
/// MRE 课件生成插件入口。
/// 继承 EasiPlugin，由希沃白板进程启动时加载。
/// </summary>
public class Program : EasiPlugin
{
    protected override Task OnRunningAsync()
    {
        // 云课件界面（课件列表页）不执行 MRE 逻辑
        if (EN.CommandOptions.IsCloud)
        {
            return Task.CompletedTask;
        }

        // Shell 端：等待 EN 就绪后注册 UI 扩展
        if (EN.App.IsReady)
        {
            Run();
        }
        else
        {
            EN.App.Ready += App_Ready;
        }

        return Task.CompletedTask;
    }

    private void App_Ready(object? sender, EventArgs e)
    {
        EN.App.Ready -= App_Ready;
        Run();
    }

    /// <summary>
    /// EN 就绪后的初始化逻辑。
    /// 延迟 3 秒确保所有内部组件初始化完毕，然后注册工具栏按钮。
    /// </summary>
    private async void Run()
    {
        await Task.Delay(TimeSpan.FromSeconds(3));

        // 在调试构建中运行 API 探索器，输出到 %TEMP%\MrePlugin_ApiDiscovery.txt
#if DEBUG
        ApiExplorer.ExploreEditingBoardApi();
#endif

        // 必须在主 UI 线程注册多语言并导出 UI 项
        System.Windows.Application.Current.Dispatcher.Invoke(() =>
        {
            ExportUIItems();
        });
    }

    /// <summary>
    /// 注册 MRE 导入按钮到希沃顶部工具栏。
    /// </summary>
    private void ExportUIItems()
    {
        var manager = Container.Current.Get<IUIItemManager>();

        // 注册菜单项及其多语言文本
        manager.AppendWithLang(
            new MreImportMenuItem(),
            new UIItemAttribute(UIItemPurposes.HeadToolBar),
            new[]
            {
                new UIItemLangInfo(new CultureInfo("zh-CHS"), "MRE导入"),
            });
    }
}
