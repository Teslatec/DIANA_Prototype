using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DentaTest.Models
{
    public interface IRepositoryModel
    {
        void SaveAsync(IFormFileCollection files);
        void SaveAsync(IFormFile file);
    }

    public class ContentRootRepository : IRepositoryModel
    {
        public void SaveAsync(IFormFileCollection files)
        {
            throw new NotImplementedException();
        }

        public void SaveAsync(IFormFile file)
        {
            throw new NotImplementedException();
        }
    }
}
