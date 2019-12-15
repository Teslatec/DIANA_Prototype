using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DentaTest.Models
{
    public class IndexResponseModel
    {
        [JsonProperty("dirtyness")]
        public float Dirtyness { get; set; }
        [JsonProperty("images")]
        public ICollection<ImageResponseModel> Images { get; set; }
    }

    public class ImageResponseModel
    {
        [JsonProperty("in")]
        public string InPath { get; set; }
        [JsonProperty("out")]
        public string OutPath { get; set; }
    }
}
