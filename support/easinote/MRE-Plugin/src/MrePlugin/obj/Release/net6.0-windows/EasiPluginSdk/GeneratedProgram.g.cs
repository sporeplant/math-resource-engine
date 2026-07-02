using dotnetCampus.EasiPlugins;
using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

// ReSharper disable CheckNamespace

namespace Cvte.EasiNote.Extensions
{
    [CompilerGenerated]
    public partial class AssemblyProvider
    {
        /// <summary>
        /// 此方法在此程序集单独运行时唤起。
        /// </summary>
        [STAThread]
#if !DEBUG_EASIPLUGIN_SDK
        [DebuggerStepThrough, DebuggerNonUserCode]
#endif
        private static int Main(string[] args)
        {
            var task = RunAsync(args);
            return task.Result;
        }

        /// <summary>
        /// 此方法在此程序集被 EasiNote 以插件形式加载时唤起。
        /// </summary>
        [DebuggerStepThrough, DebuggerNonUserCode]
        public void Run()
        {
            var args = new string[0];
            AppendEasiPluginDependencies();
            ExportAssemblyToEasiNote();
            RunAsync(args);
        }

        /// <summary>
        /// 如果编译器检测到此插件带有依赖，则会执行此方法将插件目录加入到 EasiNote 搜索目录。
        /// </summary>
        //[Conditional("PLUGIN_HAS_DEPENDENCY")]
        private void AppendEasiPluginDependencies()
        {
            var privatePath = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            AssemblyResolver.AppendDirectories(privatePath);
        }

        /// <summary>
        /// 请注意，此方法仅在目标项目引用了希沃白板依赖后才会调用；用于将插件接入到希沃白板中。
        /// </summary>
        [Conditional("PLUGIN_IS_EN_DEPENDENT")]
        private void ExportAssemblyToEasiNote()
        {
#if PLUGIN_IS_EN_DEPENDENT
            OnEasiNoteReferenced();
#endif
        }

        private static Task<int> RunAsync(string[] args)
            => EasiPluginLauncher.RunAsync(args);
    }
}
