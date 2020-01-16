using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using DentaTest.Models;
using DentaTest.Infrastructure;
using System.Threading;
using Microsoft.Extensions.Hosting;
using System.Net.Sockets;
using System.Text;
using Newtonsoft.Json;
using Microsoft.AspNetCore.Hosting;
using System.IO;
using PdfSharp.Pdf;
using PdfSharp.Drawing;
using DentaTest.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Serilog;

namespace DentaTest.Infrastructure
{
    public class RequestPipelineHandler
    {

        public async Task NewPipelineAsync(ImageRequestModel model, string traceId)
        {
            Log.Information("Request ({0}): Started new Pipiline in {1}", traceId, nameof(NewPipelineAsync));
            var index = await TcpConnectionService.TransformAsync(model, traceId);
            if (index == null)
            {
                Log.Error("Request ({0}): Pipiline ended without result in {1} because index is null", traceId, nameof(NewPipelineAsync));
                return;
            }
            
            var pdf = PdfService.ConvertToPdf(index, traceId);
            if (pdf == null)
            {
                Log.Error("Request ({0}): Pipiline ended without result in {1} because pdf is null", traceId, nameof(NewPipelineAsync));
                return;
            }
            
            var result = await EmailService.SendEmailAsync(model.Email, "DIANA - Dental Index Analysis Application", index.Dirtyness.ToString(), pdf, traceId);
            if (!result)
            {
                Log.Error("Request ({0}): Pipiline ended without result in {1} because error in email service", traceId, nameof(NewPipelineAsync));
                return;
            }
            Log.Information("Request ({0}): Ended Pipiline sucsesfully in {1}", traceId, nameof(NewPipelineAsync));
            //return;
        }
    }
}
