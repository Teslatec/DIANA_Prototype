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

                var section = document.AddSection();

                
                var header = section.Headers.Primary;
                var logoImage = header.AddImage(Directory.GetCurrentDirectory() + "/" + "logo.png");
                logoImage.LockAspectRatio = true;
                logoImage.Height = "0.8382cm";
                var paragraph = header.AddParagraph();
                paragraph.AddFormattedText("Dental Index Analysis Application", new MigraDoc.DocumentObjectModel.Font("Verdana"));

                paragraph = section.AddParagraph();
                var font = new MigraDoc.DocumentObjectModel.Font("Arial", 16);
                font.Bold = true;
                paragraph.Format.Alignment = MigraDoc.DocumentObjectModel.ParagraphAlignment.Center;
                paragraph.AddFormattedText("Результат расчёта", font);
                paragraph.Format.SpaceBefore = 24.0;
                paragraph.Format.SpaceAfter = 12.0;

                paragraph = section.AddParagraph();
                paragraph.AddFormattedText("Ф.И.О. пациента: ");
                paragraph.AddLineBreak();
                paragraph.AddFormattedText("Ф.И.О. врача: ");
                paragraph.AddLineBreak();
                paragraph.AddFormattedText("Дата приёма: ");
                paragraph.Format.LineSpacing = 12.0;
                paragraph.Format.LineSpacingRule = MigraDoc.DocumentObjectModel.LineSpacingRule.Exactly;
                paragraph.Format.SpaceAfter = 24.0;

                paragraph = section.AddParagraph();
                paragraph.Format.Shading.Color = MigraDoc.DocumentObjectModel.Colors.Yellow;
                font = new MigraDoc.DocumentObjectModel.Font("Arial", 12);
                font.Bold = true;
                paragraph.AddFormattedText(
                        string.Format("Индекс гигиены полости рта: {0}%*",
                            (Math.Round(model.Dirtyness * 100.0))), font);
                paragraph.Format.SpaceAfter = 12.0;

                var table = section.AddTable();
                for (int i = 0; i < 3; i++)
                {
                    var column = table.AddColumn();
                }
                table.Columns[0].Width = 15;
                table.Columns[2].Width = 500;
                MigraDoc.DocumentObjectModel.Tables.Row row = null;
                row = table.AddRow();
                paragraph = row.Cells[0].AddParagraph("*");
                paragraph = row.Cells[1].AddParagraph("0%-24%");
                paragraph.Format.Shading.Color = MigraDoc.DocumentObjectModel.Colors.LightGreen;
                row.Cells[2].AddParagraph("гигиена хорошая;");
                row = table.AddRow();
                paragraph = row.Cells[1].AddParagraph("25%-49%");
                paragraph.Format.Shading.Color = MigraDoc.DocumentObjectModel.Colors.Cyan;
                row.Cells[2].AddParagraph("гигиена удовлетворительная;");
                row = table.AddRow();
                paragraph = row.Cells[1].AddParagraph("50%-74%");
                paragraph.Format.Shading.Color = MigraDoc.DocumentObjectModel.Colors.Yellow;
                row.Cells[2].AddParagraph("гигиена неудовлетворительная;");
                row = table.AddRow();
                paragraph = row.Cells[1].AddParagraph("75%-100%");
                paragraph.Format.Shading.Color = MigraDoc.DocumentObjectModel.Colors.Red;
                row.Cells[2].AddParagraph("гигиена плохая,");

                paragraph = section.AddParagraph();
                paragraph.AddFormattedText("Фотопротокол полости рта:");
                paragraph.Format.SpaceBefore = 12.0;
                paragraph.Format.SpaceAfter = 12.0;

                var nColumns = 3;

                float sectionWidth = document.DefaultPageSetup.PageWidth -
                                     document.DefaultPageSetup.LeftMargin -
                                     document.DefaultPageSetup.RightMargin;

                float columnWidth = sectionWidth / nColumns;
                table = section.AddTable();
                for (int i = 0; i < nColumns; i++)
                {
                    var column = table.AddColumn();
                    column.Width = columnWidth;
                }

                var imagesDrawn = 0;
                row = null;
                foreach (var image in model.Images)
                {
                    var columnIndex = imagesDrawn % nColumns;
                    if (columnIndex == 0)
                    {
                        row = table.AddRow();
                        row.Height = 100;
                    }
                    string fullPath = _directory + image.OutPath;
                    
                    var pdfImage = row.Cells[columnIndex].AddImage(fullPath);
                    Console.WriteLine("Added an image " + fullPath);
                    pdfImage.LockAspectRatio = true;
                    pdfImage.Width = "5.0cm";
                    imagesDrawn++;
                }
                
                paragraph = section.AddParagraph();
                paragraph.Format.SpaceBefore = 12.0;
                paragraph.AddFormattedText("Рекомендации:");

                for (int i = 0; i < 5; i++)
                {
                    paragraph = section.AddParagraph();
                    paragraph.Format.Alignment = MigraDoc.DocumentObjectModel.ParagraphAlignment.Center;
                    //...any other formats needed
                    paragraph.Format.Borders.Bottom = new MigraDoc.DocumentObjectModel.Border()
                    {
                        Width = "1pt",
                        Color = MigraDoc.DocumentObjectModel.Colors.DarkGray
                    };
                    paragraph.Format.SpaceBefore = 12.0;
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
            Console.WriteLine("Created PDF document with size " + pdfBuffer.Length);
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
