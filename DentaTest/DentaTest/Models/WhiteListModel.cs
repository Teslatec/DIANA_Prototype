using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DentaTest.Models
{
    public interface IWhiteListModel
    {
        IQueryable<string> WhiteList { get; }
    }

    public class WhiteListTempModel : IWhiteListModel
    {
        public IQueryable<string> WhiteList { get; } = new List<string> { "lipranu@gmail.com", "an_romanov@teslatec.ru" }.AsQueryable();
    }
}
