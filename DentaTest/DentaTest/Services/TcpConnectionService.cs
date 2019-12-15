using DentaTest.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace DentaTest.Infrastructure
{
    public static class TcpConnectionService
    {
        static private readonly int _port = int.Parse(Environment.GetEnvironmentVariable("port") ?? "8888");
        static private readonly string _ip = Environment.GetEnvironmentVariable("ip") ?? "127.0.0.1";

        public static async Task<IndexResponseModel> TransformAsync(ImageRequestModel model)
        {
            using TcpClient client = new TcpClient(_ip, _port);
            using NetworkStream stream = client.GetStream();
            var encoding = new UTF8Encoding(false, false);
            var str = JsonConvert.SerializeObject(model);
            var data = encoding.GetBytes(str);
            stream.Write(data, 0, data.Length);
            do
            {
                await Task.Delay(100);
            } while (!stream.DataAvailable);

            StringBuilder stringBuilder = new StringBuilder();
            byte[] bytes = new byte[64];
            int buffer = 0;

            do
            {
                buffer = stream.Read(bytes, 0, bytes.Length);
                stringBuilder.Append(encoding.GetString(bytes, 0, buffer)); 
            } while (stream.DataAvailable);

            
            var response = JsonConvert.DeserializeObject<IndexResponseModel>(stringBuilder.ToString());

            return response;
        }
    }
}
