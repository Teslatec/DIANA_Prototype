using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DentaTest.Models
{
    public class PurityIndex
    {
        [JsonProperty("day")]
        public float Day { get; set; }
        [JsonProperty("week")]
        public float Week { get; set; }
        [JsonProperty("month")]
        public float Month { get; set; }
    }

    public class IndexResponseModel
    {
        [JsonProperty("purity_index")]
        public PurityIndex PurityIndex { get; set; }
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
