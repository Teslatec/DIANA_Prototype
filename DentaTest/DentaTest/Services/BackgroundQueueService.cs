using Microsoft.Extensions.Hosting;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using DentaTest.Infrastructure;
using Serilog;
using Microsoft.Extensions.Logging;

namespace DentaTest.Services
{
    public class BackgroundQueueService : BackgroundService
    {
        public BackgroundQueueService(IBackgroundQueue taskQueue)
        {
            TaskQueue = taskQueue;
        }

        public IBackgroundQueue TaskQueue { get; }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            await BackgroundProcessing(stoppingToken);
        }

        private async Task BackgroundProcessing(CancellationToken stoppingToken)
        {
            Log.Information("{0} start working", nameof(BackgroundQueueService));
            while (!stoppingToken.IsCancellationRequested)
            {
                var workItem = await TaskQueue.DequeueAsync(stoppingToken);

                try
                {
                    await workItem(stoppingToken);
                }
                catch (Exception ex)
                {
                    Log.Fatal(ex, "Error occurred executing {0} in {1}.", nameof(workItem), nameof(BackgroundProcessing));
                }
            }
        }

        public override async Task StopAsync(CancellationToken stoppingToken)
        {
            Log.Warning("{0} - stop working", nameof(BackgroundQueueService));
            await base.StopAsync(stoppingToken);
        }
    }
}
