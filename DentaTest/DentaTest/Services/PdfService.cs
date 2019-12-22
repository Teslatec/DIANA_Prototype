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
            try {
            using (var stream = new MemoryStream())
            {
                var document = new MigraDoc.DocumentObjectModel.Document();
                document.Info.Title = "Dental index";
                document.Info.Subject = "";
                document.Info.Author = "DIANA";

                var style = document.Styles["Heading1"];
                style.Font.Name = "Times New Roman";
                style.Font.Size = 16;
                style.Font.Bold = true;

                var section = document.AddSection();

                var paragraph = section.AddParagraph();
                var font = new MigraDoc.DocumentObjectModel.Font("Times New Roman", 16);
                font.Bold = true;
                paragraph.Format.Alignment = MigraDoc.DocumentObjectModel.ParagraphAlignment.Center;
                paragraph.AddFormattedText("Результаты расчёта", font);

                paragraph = section.AddParagraph("Ф.И.О. пациента: ");
                paragraph = section.AddParagraph("Ф.И.О. врача: ");
                paragraph = section.AddParagraph("Дата приёма: ");

                paragraph = section.AddParagraph();
                paragraph.Format.Shading.Color = MigraDoc.DocumentObjectModel.Colors.Yellow;
                font = new MigraDoc.DocumentObjectModel.Font("Times New Roman", 12);
                font.Bold = true;
                paragraph.AddFormattedText(
                        string.Format("Индекс гигиены полости рта: {0}%*",
                            (Math.Round(model.Dirtyness * 100.0))), font);

                paragraph = section.AddParagraph();
                paragraph.AddFormattedText("Фотопротокол полости рта");

                var nColumns = 3;

                float sectionWidth = document.DefaultPageSetup.PageWidth -
                                     document.DefaultPageSetup.LeftMargin -
                                     document.DefaultPageSetup.RightMargin;

                float columnWidth = sectionWidth / nColumns;
                var table = section.AddTable();
                for (int i = 0; i < nColumns; i++) {
                    var column = table.AddColumn();
                    column.Width = columnWidth;
                }

                var imagesDrawn = 0;
                MigraDoc.DocumentObjectModel.Tables.Row row = null;
                foreach (var image in model.Images)
                {
                    var columnIndex = imagesDrawn % nColumns;
                    if (columnIndex == 0)
                    {
                        row = table.AddRow();
                    }
                    string fullPath = _directory + image.OutPath;
                    
                    var pdfImage = row.Cells[columnIndex].AddImage(fullPath);
                    Console.WriteLine("Added an image " + fullPath);
                    pdfImage.Width = "5.0cm";
                    pdfImage.LockAspectRatio = true;
                    imagesDrawn++;
                }
                
                var renderer = new MigraDoc.Rendering.PdfDocumentRenderer(true, PdfSharp.Pdf.PdfFontEmbedding.Always);
                renderer.Document = document;
                try
                {
                    renderer.RenderDocument();
                }
                catch (Exception e)
                {
                    Console.WriteLine(e);
                }

                // Save the document...
                renderer.PdfDocument.Save(stream, false);
                pdfBuffer = stream.ToArray();
            }
            }
            catch (Exception e)
            {
                Console.WriteLine("Something bad happened");
                Console.WriteLine(e);
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
