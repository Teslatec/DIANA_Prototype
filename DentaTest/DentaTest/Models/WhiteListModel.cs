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
        public IQueryable<string> WhiteList { get; } = new List<string> 
        {
            "miata.v@gmail.com",
            "vic9103@yandex.ru",
            "ivan@teslatec.ru",
            "lipranu@gmail.com", 
            "an_romanov@teslatec.ru",
            "dianadm1@dentmaster.ru",
            "dianadm2@dentmaster.ru",
            "dianadm3@dentmaster.ru",
            "dianadm4@dentmaster.ru",
            "dianadm@dentmaster.ru"
        }.AsQueryable();
    }
}
