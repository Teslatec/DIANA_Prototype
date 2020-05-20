using DentaTest.Models;
using Serilog;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DentaTest.Infrastructure
{
    public static class PdfService
    {
        public static byte[] ConvertToPdf(IndexResponseModel model, string requestId)
        {
            Log.Information("Request ({0}): Making PDF in {1}", requestId, nameof(ConvertToPdf));


            byte[] pdfBuffer = null;
            try 
            {
                using var stream = new MemoryStream();

                string html = runPhp(model.PurityIndex);

                Console.WriteLine("HTML Output: " + html);

            }
            catch (Exception ex)
            {
                Log.Error(ex, "Request ({0}): Fail at making PDF in {1}", requestId, nameof(ConvertToPdf));
                return null;
            }

            Log.Information("Request ({0}): Created PDF document with size {1} in {2}", requestId, pdfBuffer.Length, nameof(ConvertToPdf));
            return pdfBuffer;
        }

        private static string runPhp(PurityIndex purityIndex) {
            int longTerm = (int)Math.Round((purityIndex.Week + purityIndex.Month) * 100.0);
            int daily = (int)Math.Round(purityIndex.Day * 100.0);
            int pure = 100 - longTerm - daily;
            int category;

            string phpArguments = String.Format("-d auto_prepend_file=prepend.php index.php daily_index={0} longterm_index={1} pure_index={2} category_id={3}",
                                                daily, longTerm,
                                                pure, category);
            if (longTerm < 15) {
                category = 1;
            } else if (longTerm < 50) {
                category = 2;
            } else {
                category = 3;
            }

            // FIXME: somebody break up arguments string, I don't know how
            using System.Diagnostics.Process phpProcess = new System.Diagnostics.Process();
            phpProcess.StartInfo.FileName = "/usr/bin/php";
            phpProcess.StartInfo.Arguments = phpArguments;
            phpProcess.StartInfo.UseShellExecute = false;
            phpProcess.StartInfo.RedirectStandardOutput = true;
            phpProcess.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            phpProcess.StartInfo.CreateNoWindow = true;
            phpProcess.StartInfo.WorkingDirectory = "/app/CHARTS/"; // TODO: get directory path from the environment
            phpProcess.Start();
            string output = phpProcess.StandardOutput.ReadToEnd();
            phpProcess.WaitForExit();
            return output;
        }

        private static readonly string _directory = Environment.GetEnvironmentVariable("image_dir");
    }
}
