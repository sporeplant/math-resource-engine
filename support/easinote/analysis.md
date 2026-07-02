# 希沃白板 5 原生插件开发分析

> 调研日期：2026-07-02
> 来源：EasiPlugin.Sample + EasiNote.ClientWebApi.Documentation + EasiNote.Sdk.Documentation

---

## 1. 插件形态对比

| 形态 | 技术 | 定制性 | 限制 | 适用场景 |
|------|------|--------|------|---------|
| **原生插件** | .NET 6 + WPF，程序集注入 | 最高 | 需本地安装，依赖 EasiNote 版本 | MRE 课件生成（选中） |
| Web 插件 | CEF 嵌入网页 + JS API | 中等 | 仅能插入多媒体和 Web 卡片 | 外部内容展示 |
| 配置插件 | 注册表/配置文件 | 最低 | 仅开关/配置 | 功能开关 |

**结论：MRE 课件生成应选择原生插件形态，才能实现页面创建、元素操作和批量导入。**

---

## 2. EasiPlugin.Sample 关键发现

### 2.1 插件入口

插件必须继承 `dotnetCampus.EasiPlugins.EasiPlugin`，重写 `OnRunningAsync()`：

```csharp
class Program : dotnetCampus.EasiPlugins.EasiPlugin
{
    protected override Task OnRunningAsync()
    {
        if (EN.CommandOptions.IsCloud)
        {
            // 云课件界面（课件列表）逻辑
        }
        else
        {
            // Shell 端（备课/授课）逻辑 ← MRE 主要战场
            if (EN.App.IsReady) Run();
            else EN.App.Ready += App_Ready;
        }
        return Task.CompletedTask;
    }
}
```

### 2.2 页面(Slide)访问

```csharp
var currentSlide = EN.EditingBoardApi.CurrentSlide;   // 当前页
var slides = EN.EditingBoardApi.Slides;                // 所有页面集合
```

⚠️ `Slides` 是只读集合还是可写集合，文档未明确。推测需要通过 `EN.EditingBoardApi` 的特定方法创建新页面。

### 2.3 元素(Element)访问

```csharp
var firstTextElement = currentSlide.Elements.OfType<TextElement>().FirstOrDefault();
foreach (var groupElement in currentSlide.Elements.OfType<GroupElement>())
{
    foreach (var textElement in groupElement.Elements.OfType<TextElement>()) { }
}
```

关键元素类型（从 sample 代码推断）：
- `TextElement` — 文本框元素（`Cvte.Paint.Features.Elements.Texts`）
- `GroupElement` — 组合元素
- 应有 `ImageElement`、`ShapeElement` 等（需实际安装 EN 后通过程序集反射确认）

### 2.4 元素坐标与尺寸

```csharp
element.Bounds = new Rect(position, size);
```

坐标系：页面左上角为原点，`Bounds` 控制元素在页面上的位置和大小。

### 2.5 文本元素详情

```csharp
var charCount = firstTextElement.TextEditor.CharCount;
var bounds = firstTextElement.TextEditor.GetRunBoundsByDocumentOffset(i);
```

`TextEditor` 提供文本内容的字符级别访问。

### 2.6 UI 扩展注册

```csharp
var manager = Container.Current.Get<IUIItemManager>();
manager.AppendWithLang(new EasiPluginSampleElementToolMenuItem(),
    new UIItemAttribute(UIItemPurposes.BoardEditMenu), new[]
    {
        new UIItemLangInfo(new CultureInfo("zh-CHS"), "演示工具")
    });
```

UI 扩展类型：
- `UIItemPurposes.HeadToolBar` — 顶部工具栏
- `UIItemPurposes.BoardEditMenu` — 右键菜单
- `UIItemPurposes.ElementEditMenu` — 元素编辑菜单

### 2.7 安装包生成

构建项目后，`bin\[Debug|Release]` 目录下自动生成：
- **exe 包**：独立安装包（.NET 6，双击安装）
- **zip 包**：插件文件归档
- **enp 包**：发布到希沃应用中心的包（zip 改后缀）

### 2.8 导出现有课件

```csharp
var storageModel = await EN.CurrentBoardApi.GetStorageModelAsync();
Container.Current.Get<IEnbxStorageProvider>().ExportEnb(storageModel.Model, filePath);
```

---

## 3. 开发环境要求

| 项目 | 要求 |
|------|------|
| IDE | Visual Studio 2022 17.5.2+ |
| .NET | .NET 6.0 + WPF |
| 希沃白板 | 最新版，安装到默认 C 盘 |
| 系统 | Win10+ |
| NuGet 包 | `dotnetCampus.EasiPlugin.Sdk`（最新稳定版 0.44.x） |
| csproj 配置 | `<UseEasiNote>all</UseEasiNote>` |

---

## 4. MRE 插件 API 需求映射

### 4.1 已知可用 API

| MRE 需求 | EasiNote API | 状态 |
|----------|-------------|------|
| 读取当前页面 | `EN.EditingBoardApi.CurrentSlide` | ✅ 已确认 |
| 读取所有页面 | `EN.EditingBoardApi.Slides` | ✅ 已确认 |
| 获取页面元素 | `Slide.Elements.OfType<T>()` | ✅ 已确认 |
| 修改元素位置/大小 | `element.Bounds = new Rect(pos, size)` | ✅ 已确认 |
| 注册菜单项 | `IUIItemManager.AppendWithLang()` | ✅ 已确认 |
| 导出课件 | `GetStorageModelAsync()` + `ExportEnb()` | ✅ 已确认 |
| 页面坐标系 | 左上角原点 | ✅ 已确认 |

### 4.2 ✅ 已验证 API（通过 MetadataLoadContext 反射 EasiNote5_5.2.4.9801）

#### Slide（页面）

```csharp
// 构造
var slide = new Slide();               // 无参
var slide = new Slide("slide_01");     // 带 ID

// 属性
slide.Id;          // string — 页面唯一 ID
slide.Title;       // string — 页面标题
slide.Elements;    // ReadOnlyCollection<Element> — 元素集合（只读）
slide.Background;  // Brush — 背景

// 元素管理
slide.Add(element);                    // 添加单个元素
slide.Add(elements);                   // 批量添加
slide.Remove(element);                 // 移除
slide.RemoveAll();                     // 清空
```

#### Board（画板 — 页面容器）

```csharp
// 通过 EN.EditingBoardApi 获取 Board 实例
board.Slides;              // SlideCollection — 所有页面
board.CurrentSlide;        // Slide — 当前页面
board.DefaultSlideSize;    // Size — 默认页面尺寸

// 页面操作
board.Insert(slide);                    // 追加到末尾
board.InsertAt(slide, index);           // 插入到指定位置
board.Insert(slides);                   // 批量追加
board.GetSlideById("slide_01");         // 按 ID 查找
board.GetSlide(index);                   // 按索引查找
```

#### TextElement（文本框）

```csharp
// 构造
var text = new TextElement();
var text = new TextElement(isEditable: true);

// 位置和大小
// 继承自 Element 基类（通过 ITransformedBounds 接口）
text.Bounds = new Rect(x, y, width, height);

// 文本内容 — 通过 TextEditor 设置
text.TextEditor.SetRichText(new RichTextSaveInfo
{
    Text = "内容文本",
    SizeToContent = SizeToContent.WidthAndHeight,
}, withForceRedraw: false);

// 获取纯文本
var saveInfo = text.TextEditor.GetRichText();
string content = saveInfo.Text;
```

#### ShapeElement（形状）

```csharp
var rect = new ShapeElement(ShapeType.Rectangle);
var ellipse = new ShapeElement(ShapeType.Ellipse);
var line = new ShapeElement(ShapeType.Line);

// 也支持贝塞尔曲线
text.Bounds = new Rect(x, y, w, h);
```

#### ImageElement（图片）⚠️

```
当前为 internal 类型，公开 API 不直接暴露。
需通过反射或 BoardService.AddResource() 间接创建。
```

#### RichTextSaveInfo（富文本数据）

```csharp
var info = new RichTextSaveInfo
{
    Text = "纯文本内容",          // string
    Paragraphs = paragraphs,        // List<ParagraphSaveInfo> — 段落级格式
    SizeToContent = ...,            // 自动调整大小
    ArrangingType = ...,            // 排列方式
};
```

### 4.3 ⚠️ 待验证（需在 EN 运行时测试）

| MRE 需求 | 推测 API | 验证方式 |
|----------|---------|---------|
| 新建页面 | `EN.EditingBoardApi.CreateSlide()` 或 `Slides.Add()` | 程序集反射 |
| 创建文本框 | `TextElement` 构造函数 | 程序集反射 |
| 创建图片元素 | `ImageElement` 构造函数 | 程序集反射 |
| 创建形状元素 | `ShapeElement` 构造函数 | 程序集反射 |
| 添加元素到页面 | `Slide.Elements.Add(element)` | 程序集反射 |
| 删除页面 | `Slides.Remove()` 或 API 方法 | 程序集反射 |
| 元素 ID | 元素的唯一标识属性 | 程序集反射 |

### 4.3 MRE lesson.json 到 EasiNote 的映射

```json
{
  "slides": [
    {
      "id": "slide_01",
      "elements": [
        {
          "id": "el_01",
          "type": "text",
          "text": "21.1 一元二次方程",
          "x": 100, "y": 50,
          "width": 800, "height": 60,
          "fontSize": 28,
          "bold": true
        },
        {
          "id": "el_02",
          "type": "image",
          "src": "assets/img_01.png",
          "x": 50, "y": 150,
          "width": 900, "height": 500
        }
      ]
    }
  ]
}
```

---

## 5. 版本兼容性风险

| 风险 | 等级 | 说明 |
|------|------|------|
| EasiNote 版本锁定 | 🔴 高 | SDK 版本与 EN 版本严格对应，升级 EN 可能导致插件失效 |
| 内部 API 不稳定 | 🟡 中 | 大量 API 未公开文档，通过反射访问可能在版本更新中变化 |
| .NET Runtime 依赖 | 🟢 低 | SDK 2.1.1+ 复用 EN 的 .NET 6 Runtime |
| NuGet 包更新慢 | 🟡 中 | SDK 版本滞后于 EN 主版本 |

---

## 7. 辅助仓库发现

### 7.1 ENAnalyzer / EasiNotePacker — .enbx 格式

- `.enbx` = ZIP 压缩包，包含 `[Content_Types].xml` + `Slides/Slide_X.xml` + 资源文件
- 希沃本地缓存路径：`%APPDATA%\Seewo\EasiNote5\Data`
- 可参考这两个工具实现离线生成 .enbx 文件（无需运行 EN 即可生成课件）
- ENAnalyzer 用 Python + wxPython，功能完善；EasiNotePacker 用 C++，代码简单

### 7.2 easinote-mcp-guide — MCP 探索

- 希沃有 `EasiNote.McpServer.dll`，配置文件在 `%APPDATA%\Seewo\SeewoAIVoiceAssistant\McpServers\`
- 使用 HTTP 协议（随机端口），但连接不稳定
- 目前不成熟，不宜作为 MRE 主路径

### 7.3 awesome-iwb

- 教学一体机软件清单，其中 Ink Canvas 系列是替代白板软件
- 与 MRE 插件开发无直接关系，可作为能力增强的参考

---

## 8. 关键缺失：元素/页面创建 API

这是当前最大的不确定性。EasiPlugin.Sample 展示了如何**读取**已有页面和元素，但**未展示如何创建**。

### 需要在 EasiNote 环境中验证的事项（按优先级排列）

| 优先级 | 验证目标 | 验证方法 |
|--------|---------|---------|
| 🔴 P0 | `Slide` 的创建方式 | 安装 EN → 反射 `EN.EditingBoardApi` 类型 → 查找 CreateSlide/AddSlide/InsertSlide 方法 |
| 🔴 P0 | `TextElement` 的创建和文本设置 | 反射 TextElement 构造函数和属性 → 查找 Text/Content/FontSize 等属性 |
| 🟡 P1 | `ImageElement` 的创建和图片源设置 | 反射 ImageElement 类型 → 查找 Source/ImageSource/Picture 等属性 |
| 🟡 P1 | `ShapeElement` 的创建 | 反射查找形状相关的元素类型 |
| 🟡 P1 | `Slide.Elements` 的可写性 | 检查 Elements 是否为可写集合（ObservableCollection/IList） |
| 🟢 P2 | 元素 ID 属性 | 查找可用于建立映射的唯一标识属性 |
| 🟢 P2 | 批量操作是否需事务 | 测试连续创建多页是否稳定 |

### 推荐验证工具

1. **dotPeek**（JetBrains 免费反编译器）：反编译 `EasiNote\Main\*.dll` 查看内部 API
2. **Visual Studio 调试器**：附加到 EasiNote.exe 进程，通过 Immediate Window 探索类型
3. **反射脚本**：在插件中编写反射代码，遍历 `EN.EditingBoardApi` 的类型和方法

### 备选路径：离线生成 .enbx

如果原生插件 API 受限，可以考虑：
1. 使用 EasiNotePacker 的思路，直接生成 .enbx 文件（ZIP + XML）
2. 研究 `Slides/Slide_X.xml` 的 XML Schema
3. 构建完整的 .enbx 生成器，脱离 EasiNote 运行

---

## 6. MVP 边界

MVP 插件将实现：

1. ✅ 在顶部工具栏注册"MRE 导入"按钮
2. ✅ 用户点击后弹出文件选择对话框，选择 `lesson.json`
3. ✅ 解析 JSON，读取 slides 数组
4. ✅ 在当前课件末尾新建一页（封面试探）
5. ✅ 在该页插入一个标题文本框
6. ✅ 构建产出 exe 安装包

后续迭代：
- 完整 JSON → 元素映射（文本、图片、公式图片、形状）
- `mre_element_id` ↔ EasiNote element 的映射表持久化
- 增量更新支持
- 批处理多页面创建
