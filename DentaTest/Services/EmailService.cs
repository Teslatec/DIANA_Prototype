using MailKit.Net.Smtp;
using Microsoft.AspNetCore.Http;
using MimeKit;
using PdfSharp.Pdf;
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
        
        public static async Task SendEmailAsync(string email, string subject, string message, byte[] pdf)
        {
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
                await client.ConnectAsync(_smtpService, _smtpServicePort, false);
                await client.AuthenticateAsync(_smtpLogin, _smtpPassword);
                await client.SendAsync(emailMessage);
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }

            await client.DisconnectAsync(true);
        }
    }
}
