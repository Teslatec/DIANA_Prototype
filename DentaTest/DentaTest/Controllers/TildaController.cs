using DentaTest.Infrastructure;
using DentaTest.Models;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Serilog;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace DentaTest.Controllers
{
    [Route("api/[controller]")]
    public class TildaController : Controller
    {
        private readonly IBackgroundQueue _backgroundQueue;
        private readonly IWhiteListModel _whiteList;
        private readonly IWebHostEnvironment _environment;

        public TildaController(IBackgroundQueue queue, IWhiteListModel whiteList, IWebHostEnvironment env)
        {
            _backgroundQueue = queue;
            _whiteList = whiteList;
            _environment = env;
        }

        [HttpPost]
        [RequestSizeLimit(52428800)]
        public async Task<IActionResult> Post(RequestModel requestModel)
        {
            Log.Information("{0}: New request started from {1}", HttpContext.TraceIdentifier, nameof(Post));
            if (!ModelState.IsValid)
            {
                Log.Warning("Request: ({0}): Invalid Model ({1}) in {2}", HttpContext.TraceIdentifier, nameof(RequestModel), nameof(Post));
                return BadRequest();
            }
            if (!_whiteList.WhiteList.Contains(requestModel.Email.ToLower()))
            {
                Log.Warning("Request ({0}): Invalid email in {1}", HttpContext.TraceIdentifier, nameof(Post));
                return BadRequest();
            }
            var directory = Environment.GetEnvironmentVariable("image_dir") ?? $@"{_environment.ContentRootPath}\FileRepository\";
            var imgRequest = new ImageRequestModel
            {
                Email = requestModel.Email,
                Images = new List<ImageModel>()
            };
            foreach (var file in requestModel.Files)
            {
                if (file != null)
                {
                    var name = Guid.NewGuid().ToString() + ".jpg";
                    var path = directory + name;
                    using (var stream = new FileStream(path, FileMode.Create))
                    {
                        try
                        {
                            await file.CopyToAsync(stream);
                        }
                        catch (Exception ex)
                        {
                            Log.Error(ex, "Request ({0}): failed to copy file ({1}) in {2}", HttpContext.TraceIdentifier, path, nameof(Post));
                            return BadRequest();
                        }
                        finally
                        {
                            stream.Close();
                            stream.Dispose();
                        }
                    }
                    var fileModel = new ImageModel { Name = name, Path = path };
                    imgRequest.Images.Add(fileModel);
                }
            }
            _backgroundQueue.QueueBackgroundWorkItem(async token =>
                await new RequestPipelineHandler().NewPipelineAsync(imgRequest, HttpContext.TraceIdentifier));
            return Ok();
        }
    }
}
