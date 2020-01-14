using DentaTest.Models;
using PdfSharp.Drawing;
using PdfSharp.Pdf;
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
                    paragraph.AddFormattedText("Дата и время приёма: " +
                           System.DateTime.Now.ToString(new System.Globalization.CultureInfo("ru-RU")));
                    paragraph.Format.LineSpacing = 12.0;
                    paragraph.Format.LineSpacingRule = MigraDoc.DocumentObjectModel.LineSpacingRule.Exactly;
                    paragraph.Format.SpaceAfter = 24.0;

                    int hygieneIndex = (int)Math.Round(model.Dirtyness * 100.0);
                    paragraph = section.AddParagraph();
                    paragraph.Format.Shading.Color = hygieneIndexToColor(hygieneIndex);
                    font = new MigraDoc.DocumentObjectModel.Font("Arial", 12);
                    font.Bold = true;
                    paragraph.AddFormattedText(
                            string.Format("Индекс гигиены полости рта: {0}%*",
                                hygieneIndex), font);
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
                    paragraph = row.Cells[1].AddParagraph(percentageRangeString(0));
                    paragraph.Format.Shading.Color = indexColors[0];
                    row.Cells[2].AddParagraph("гигиена хорошая;");
                    row = table.AddRow();
                    paragraph = row.Cells[1].AddParagraph(percentageRangeString(1));
                    paragraph.Format.Shading.Color = indexColors[1];
                    row.Cells[2].AddParagraph("гигиена удовлетворительная;");
                    row = table.AddRow();
                    paragraph = row.Cells[1].AddParagraph(percentageRangeString(2));
                    paragraph.Format.Shading.Color = indexColors[2];
                    row.Cells[2].AddParagraph("гигиена неудовлетворительная;");
                    row = table.AddRow();
                    paragraph = row.Cells[1].AddParagraph(percentageRangeString(3));
                    paragraph.Format.Shading.Color = indexColors[3];
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
                        Log.Information("Request ({0}): Rendering PDF in {1}", requestId, nameof(ConvertToPdf));
                        renderer.RenderDocument();
                        renderer.PdfDocument.Save(stream, false);
                        pdfBuffer = stream.ToArray();
                    }
                    catch (Exception ex)
                    {
                        Log.Error(ex, "Request ({0}): Failed at render PDF in {1}", requestId, nameof(ConvertToPdf));
                        return null;
                    }
                    finally
                    {
                        stream.Close();
                        stream.Dispose();
                    }
                }
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Request ({0}): Fail at making PDF in {1}", requestId, nameof(ConvertToPdf));
                return null;
            }

            Log.Information("Request ({0}): Created PDF document with size {1} in {2}", requestId, pdfBuffer.Length, nameof(ConvertToPdf));
            return pdfBuffer;
        }

        private static readonly string _directory = Environment.GetEnvironmentVariable("image_dir");

        private static readonly MigraDoc.DocumentObjectModel.Color[] indexColors = new MigraDoc.DocumentObjectModel.Color[]
        {
            MigraDoc.DocumentObjectModel.Colors.ForestGreen,
            MigraDoc.DocumentObjectModel.Colors.Cyan,
            MigraDoc.DocumentObjectModel.Colors.Yellow,
            MigraDoc.DocumentObjectModel.Colors.Red,
        };
        private static readonly int[] indexThresholds = new int[] {25, 50, 75};

        /* index argument: index in indexThresholds array */
        private static string percentageRangeString(int index) {
            double low = index <= 0 ? 0 : indexThresholds[index - 1] - 1;
            double high = index >= (indexThresholds.Length - 1) ? 
                                    100 : indexThresholds[index];
            return string.Format("{0}-{1}%", low, high);
        }

        private static MigraDoc.DocumentObjectModel.Color hygieneIndexToColor(int hygieneIndex) {
            int i = 0;
            while (i < indexThresholds.Length && indexThresholds[i] <= hygieneIndex) {
                i++;
            }
            
            if (i >= indexThresholds.Length) {
                i = indexThresholds.Length - 1;
            }

            return indexColors[i];
        }
    }
}
