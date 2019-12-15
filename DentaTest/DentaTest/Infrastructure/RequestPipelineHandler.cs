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

namespace DentaTest.Infrastructure
{
    public class RequestPipelineHandler
    {
        public async Task NewPipelineAsync(ImageRequestModel model)
        {

            var index = await TcpConnectionService.TransformAsync(model);
            var pdf = PdfService.ConvertToPdf(index);
            await EmailService.SendEmailAsync(model.Email, "DIANA - Dental Index Analysis Application", index.Dirtyness.ToString(), pdf);
        }

        //public async Task<ImageRequestModel> TransformAsync(ImageRequestModel model, string ip, int port)
        //{
        //    using TcpClient client = new TcpClient(ip, port);
        //    using NetworkStream stream = client.GetStream();
        //    var str = JsonConvert.SerializeObject(model);
        //    var enc = new UTF8Encoding(false, false);
        //    var data = enc.GetBytes(str);
        //    stream.Write(data, 0, data.Length);
        //    do
        //    {
        //        await Task.Delay(1000);
        //    } while (!stream.DataAvailable);

        //    StringBuilder stringBuilder = new StringBuilder();
        //    byte[] bytes = new byte[64];
        //    int buffer = 0;

        //    do
        //    {
        //        buffer = stream.Read(bytes, 0, bytes.Length);
        //        stringBuilder.Append(enc.GetString(bytes, 0, buffer));
        //    } while (stream.DataAvailable);

        //    var output = JsonConvert.DeserializeObject<ImageRequestModel>(stringBuilder.ToString());

        //    return output;
        //}
    }
}
