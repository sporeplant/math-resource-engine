using System.Collections.Generic;
using Cvte.Paint.Features.Elements;

namespace EasiPlugin.MRE
{
    public class ElementMapper
    {
        private readonly Dictionary<string, Element> _map = new();

        public void Register(string mreElementId, Element enElement)
        {
            _map[mreElementId] = enElement;
        }

        public bool TryGetEnElement(string mreElementId, out Element? enElement)
        {
            return _map.TryGetValue(mreElementId, out enElement);
        }

        public Element? GetEnElement(string mreElementId)
        {
            return _map.GetValueOrDefault(mreElementId);
        }

        public IReadOnlyDictionary<string, Element> AllMappings => _map;

        public void Clear()
        {
            _map.Clear();
        }

        public bool Remove(string mreElementId)
        {
            return _map.Remove(mreElementId);
        }
    }
}
