using MailKit.Net.Smtp;
using Microsoft.AspNetCore.Http;
using MimeKit;
using PdfSharp.Pdf;
using Serilog;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace DentaTest.Services
{
    public static class EmailService
    {
        private static readonly string _smtpService = 
            Environment.GetEnvironmentVariable("smtp_service") ?? "smtp.yandex.ru";
        private static readonly int _smtpServicePort = 
            int.Parse(Environment.GetEnvironmentVariable("smtp_service_port") ?? "25");
        private static readonly string _smtpLogin = 
            Environment.GetEnvironmentVariable("smtp_login") ?? "denta.noreply@yandex.ru";
        private static readonly string _smtpPassword = 
            Environment.GetEnvironmentVariable("smtp_password") ?? "hxbplcxbeazbwzat";
        
        public static async Task<bool> SendEmailAsync(string email, string subject, string message, byte[] pdf, string requestId)
        {
            Log.Information("Request ({0}): Sending email in {1}", requestId, nameof(SendEmailAsync));
            var emailMessage = new MimeMessage();

            emailMessage.From.Add(new MailboxAddress("DIANA - Dental Index Analysis Application", _smtpLogin));
            emailMessage.To.Add(new MailboxAddress("", email));
            emailMessage.Subject = subject;
            var body = new BodyBuilder();
            body.Attachments.Add($"Diana_{DateTime.Now}.pdf", pdf);
            body.TextBody = message;
            emailMessage.Body = body.ToMessageBody();

            using var client = new SmtpClient();
            try
            {
                Log.Information("Request ({0}): Try connect to smtp in {1}", requestId, nameof(SendEmailAsync));
                await client.ConnectAsync(_smtpService, _smtpServicePort, false);
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Request ({0}): Failed at connect to smtp in {1}", requestId, nameof(SendEmailAsync));
                return false;
            }

            try
            {
                Log.Information("Request ({0}): Try authenticate to smtp in {1}", requestId, nameof(SendEmailAsync));
                await client.AuthenticateAsync(_smtpLogin, _smtpPassword);
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Request ({0}): Failed at authenticate to smtp in {1}", requestId, nameof(SendEmailAsync));
                return false;
            }

            try
            {
                await client.SendAsync(emailMessage);
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Request ({0}): Failed at sending message to smtp in {1}", requestId, nameof(SendEmailAsync));
                return false;
            }

            await client.DisconnectAsync(true);

            return true;
        }
    }
}
