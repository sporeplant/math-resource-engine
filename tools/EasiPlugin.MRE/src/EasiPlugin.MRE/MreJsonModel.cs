using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace EasiPlugin.MRE
{
    public class LessonPackage
    {
        [JsonPropertyName("lesson_id")]
        public string LessonId { get; set; } = string.Empty;

        [JsonPropertyName("lesson_name")]
        public string LessonName { get; set; } = string.Empty;

        [JsonPropertyName("pages")]
        public List<LessonPage> Pages { get; set; } = new();
    }

    public class LessonPage
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;

        [JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;

        [JsonPropertyName("elements")]
        public List<LessonElement> Elements { get; set; } = new();

        [JsonPropertyName("background_color")]
        public string? BackgroundColor { get; set; }
    }

    public class LessonElement
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;

        [JsonPropertyName("type")]
        public string Type { get; set; } = string.Empty;

        [JsonPropertyName("content")]
        public string? Content { get; set; }

        [JsonPropertyName("x")]
        public double X { get; set; }

        [JsonPropertyName("y")]
        public double Y { get; set; }

        [JsonPropertyName("width")]
        public double Width { get; set; }

        [JsonPropertyName("height")]
        public double Height { get; set; }

        [JsonPropertyName("style")]
        public ElementStyle? Style { get; set; }

        [JsonPropertyName("image_path")]
        public string? ImagePath { get; set; }

        [JsonPropertyName("shape_type")]
        public string? ShapeType { get; set; }

        [JsonPropertyName("children")]
        public List<LessonElement>? Children { get; set; }
    }

    public class ElementStyle
    {
        [JsonPropertyName("font_size")]
        public double? FontSize { get; set; }

        [JsonPropertyName("font_weight")]
        public string? FontWeight { get; set; }

        [JsonPropertyName("text_align")]
        public string? TextAlign { get; set; }

        [JsonPropertyName("color")]
        public string? Color { get; set; }

        [JsonPropertyName("background_color")]
        public string? BackgroundColor { get; set; }

        [JsonPropertyName("border_color")]
        public string? BorderColor { get; set; }

        [JsonPropertyName("border_width")]
        public double? BorderWidth { get; set; }

        [JsonPropertyName("opacity")]
        public double? Opacity { get; set; }
    }
}
