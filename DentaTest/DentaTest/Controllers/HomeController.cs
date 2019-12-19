using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using DentaTest.Models;
using DentaTest.Infrastructure;
using Microsoft.AspNetCore.Hosting;
using System.IO;
using Microsoft.Extensions.Hosting;
using System.Text;

namespace DentaTest.Controllers
{
    public class HomeController : Controller
    {
        private readonly IBackgroundQueue backgroundQueue;
        private readonly IWhiteListModel whiteList;
        private readonly IWebHostEnvironment environment;
        private IHostApplicationLifetime _lifetime;

        public HomeController(
            IBackgroundQueue queue, 
            IWhiteListModel white, 
            IWebHostEnvironment env, 
            IHostApplicationLifetime hst)
        {
            backgroundQueue = queue;
            whiteList = white;
            environment = env;
            _lifetime = hst;
        }

        public IActionResult Index()
        {
            return View();
        }

        public IActionResult Privacy()
        {
            return View();
        }

        [HttpPost]
        //[ServiceFilter(typeof(EmailFilter))]
        [RequestSizeLimit(52428800)]
        public async Task<IActionResult> AddToQueue(RequestModel requestModel)
        {
            if(!whiteList.WhiteList.Contains(requestModel.Email.ToLower()))
            {
                TempData["message"] = "Email не зарегестрирован";
                return View("Index");
            }
            if(!ModelState.IsValid)
            {
                return View("Index");
            }
            var directory = Environment.GetEnvironmentVariable("image_dir") ?? $@"{environment.ContentRootPath}\FileRepository\";
            var imgRequest = new ImageRequestModel
            {
                Email = requestModel.Email,
                Images = new List<ImageModel>()
            };
            foreach(var file in requestModel.Files)
            {
                if (file != null)
                {
                    var name = Guid.NewGuid().ToString() + ".jpg";
                    var path = directory + name;
                    using (var stream = new FileStream(path, FileMode.Create))
                    {
                        await file.CopyToAsync(stream);
                    }
                    var fileModel = new ImageModel { Name = name, Path = path };
                    imgRequest.Images.Add(fileModel);
                }
            }
            backgroundQueue.QueueBackgroundWorkItem(async token => 
                await new RequestPipelineHandler().NewPipelineAsync(imgRequest));
            return RedirectToAction("Index");
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
