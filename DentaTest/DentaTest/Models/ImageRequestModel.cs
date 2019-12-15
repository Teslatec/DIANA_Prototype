using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DentaTest.Models
{
    public class ImageRequestModel
    {
        public int Id { get; set; }

        public string Email { get; set; }

        public ICollection<ImageModel> Images { get; set; }

    }
}
