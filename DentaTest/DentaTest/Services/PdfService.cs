using DentaTest.Models;
using PdfSharp.Drawing;
using PdfSharp.Pdf;
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
        private static readonly string _directory = Environment.GetEnvironmentVariable("image_dir");

        public static byte[] ConvertToPdf(IndexResponseModel model)
        {
            byte[] pdfBuffer = null;
            using (var stream = new MemoryStream())
            {
                using var document = new PdfDocument();
                //var page = document.AddPage();
                //using var gfx = XGraphics.FromPdfPage(page);
                //gfx.MUH = PdfFontEncoding.Unicode;
                //InsertLogo(gfx, null);
                //double y = 0;
                foreach (var image in model.Images)
                {
                    string fullPath = _directory + image.OutPath;
                    try
                    {
                        var page = document.AddPage();
                        using var gfx = XGraphics.FromPdfPage(page);
                        using var xImage = XImage.FromFile(fullPath);
                        double y = 100;
                        double x = 100; // (250 - xImage.PixelWidth * 72 / xImage.HorizontalResolution) / 2;
                        gfx.DrawImage(xImage, x, y);
                        //y += xImage.PixelHeight + 10;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex);
                    }
                }
                //Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                document.Save(stream, false);
                document.Close();
                pdfBuffer = stream.ToArray();
            }
            return pdfBuffer;
        }

        //private void InsertLogo(XGraphics gfx, string logoPath, PdfDocument doc)
        //{
        //    XRect rect = new XRect(new XPoint(), gfx.PageSize);
        //    rect.Inflate(-10, -15);
        //    XFont font = new XFont("Arial", 8, XFontStyle.Regular);
        //    gfx.DrawString("Dental Index Analysis Application", font, XBrushes.Black, rect, XStringFormats.TopRight);
            
        //    rect.Offset(0, 5);
        //    font = new XFont("Verdana", 8, XFontStyle.Italic);
        //    XStringFormat format = new XStringFormat();
        //    format.Alignment = XStringAlignment.Near;
        //    format.LineAlignment = XLineAlignment.Far;
        //    gfx.DrawString("Created with " + PdfSharp.ProductVersionInfo.Producer, font, XBrushes.DarkOrchid, rect, format);

        //    font = new XFont("Verdana", 8);
        //    format.Alignment = XStringAlignment.Center;
        //    gfx.DrawString(Program.s_document.PageCount.ToString(), font, XBrushes.DarkOrchid, rect, format);

        //    doc.Outlines.Add(title, page, true);
        //}
        
    }
}
