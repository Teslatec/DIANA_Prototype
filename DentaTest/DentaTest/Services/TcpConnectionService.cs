using DentaTest.Models;
using Newtonsoft.Json;
using Serilog;
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

        public static async Task<IndexResponseModel> TransformAsync(ImageRequestModel model, string requestId)
        {
            Log.Information("Request ({0}): Start tcp connection task in {1}", requestId, nameof(TransformAsync));
            try
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

                IndexResponseModel response;

                try
                {
                    response = JsonConvert.DeserializeObject<IndexResponseModel>(stringBuilder.ToString());
                }
                catch (Exception ex)
                {
                    Log.Error(ex, "Request ({0}): Deserialize exception in {1}", requestId, nameof(TransformAsync));
                    return null;
                }

                return response;
            }
            catch (Exception ex)
            {
                Log.Fatal(ex, "Request {0}: TCP task failed in {1}", requestId, nameof(TransformAsync));
                return null;
            }
        }
    }

    //public class ControllerConnectionService : IDisposable
    //{
    //    private static readonly byte[] _pingBytes = Encoding.UTF8.GetBytes(GetMessageString(MessageType.Ping, string.Empty));

    //    private SimpleTcpClient _tcpClient;

    //    private Timer _pingTimer;

    //    public ControllerConnectionService()
    //    {
    //        Create();
    //    }

    //    public void Dispose()
    //    {
    //        Close();
    //    }

    //    public event EventHandler<DataModel> ContentTypeChanged;

    //    private MainViewModel MainViewModel { get; } = new MainViewModel { Id = 1 };
    //    private int ClientControllerPort { get; } = 8080;

    //    private string ControllerIp { get; } = "127.0.0.1";

    //    private static DateTime DateStamp => DateTime.UtcNow;

    //    private void Create()
    //    {
    //        if (_tcpClient == null)
    //        {
    //            _tcpClient = new SimpleTcpClient();
    //            _tcpClient.DataReceived += TcpClientOnDataReceived;
    //        }

    //        if (_pingTimer == null)
    //        {
    //            _pingTimer = new Timer { Interval = 2000 };
    //            _pingTimer.Elapsed += PingTimerOnElapsed;
    //        }
    //    }

    //    private void Close()
    //    {
    //        if (_pingTimer != null)
    //        {
    //            _pingTimer.Elapsed -= PingTimerOnElapsed;
    //            _pingTimer.Dispose();
    //            _pingTimer = null;
    //        }

    //        if (_tcpClient != null)
    //        {
    //            _tcpClient.DataReceived -= TcpClientOnDataReceived;
    //            _tcpClient.Dispose();
    //            _tcpClient = null;
    //        }
    //    }

    //    public void Initialize()
    //    {
    //        Connect();

    //        var messageString = GetMessageString(MessageType.SendId, MainViewModel.Id.ToString());
    //        SendMessage(messageString);

    //        _pingTimer.Start();
    //    }

    //    private void PingTimerOnElapsed(object sender, ElapsedEventArgs elapsedEventArgs)
    //    {
    //        if (!IsConnected()) Reconnect();
    //    }

    //    private bool IsConnected()
    //    {
    //        try
    //        {
    //            _tcpClient.TcpClient.Client.Send(_pingBytes);
    //            return true;
    //        }
    //        catch (Exception)
    //        {
    //            return false;
    //        }
    //    }

    //    private void Connect()
    //    {
    //        try
    //        {
    //            _tcpClient.Connect(ControllerIp, ClientControllerPort);
    //        }
    //        catch (Exception)
    //        {
    //            Reconnect();
    //        }
    //    }

    //    private void Reconnect()
    //    {
    //        try
    //        {
    //            while (!IsConnected())
    //            {
    //                Thread.Sleep(500);
    //                Close();
    //                Create();

    //                _tcpClient.Connect(ControllerIp, ClientControllerPort);
    //            }
    //        }
    //        catch (Exception)
    //        {
    //            // This is recursion and an exceptional condition above will cause a Stack Overflow.
    //            // Implement a "number of retries" before just throwing the exception and letting the
    //            // caller handle it.
    //            Reconnect();
    //        }
    //    }

    //    private void SendMessage(string message)
    //    {
    //        try
    //        {
    //            _tcpClient.TcpClient.Client.Send(Encoding.UTF8.GetBytes(message));
    //        }
    //        catch (Exception)
    //        {
    //            Reconnect();
    //        }
    //    }

    //    private void TcpClientOnDataReceived(object sender, Message message)
    //    {
    //        if (string.IsNullOrEmpty(message.MessageString))
    //            return;

    //        var messageParts = message.MessageString.Split(';');

    //        Enum.TryParse(messageParts[0], out MessageType messagetype);

    //        if (messagetype == MessageType.UpdateContentType)
    //        {
    //            Console.WriteLine($@"{DateStamp} Data received: {message.MessageString} ");
    //            var dataModel = JsonConvert.DeserializeObject<DataModel>(messageParts[1]);

    //            ContentTypeChanged?.Invoke(this, dataModel);
    //        }
    //    }

    //    private static string GetMessageString(MessageType messageType, string data)
    //    {
    //        return messageType + ":" + data;
    //    }
    //}
}
