using DentaTest.Controllers;
using DentaTest.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DentaTest.Infrastructure
{
    public class EmailFilter : ActionFilterAttribute
    {
        private readonly IWhiteListModel whiteList;
        
        public override void OnActionExecuting(ActionExecutingContext context)
        {
            if (!whiteList.WhiteList.Contains(
                (context.ActionArguments[nameof(RequestModel)] as RequestModel)?.Email.ToLower()))
            {
                (context.Controller as Controller).TempData["message"] = "Email не зарегестрирован";
                context.Result = new RedirectToActionResult(nameof(HomeController.Index), nameof(HomeController), null);
            }
        }
    }
}
