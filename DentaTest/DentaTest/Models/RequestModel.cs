using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using DentaTest.Infrastructure;

namespace DentaTest.Models
{
    public class RequestModel
    {
        public Guid Id { get; set; } = Guid.NewGuid();

        [Required(AllowEmptyStrings = false, ErrorMessage = "Введите email")]
        public string Email { get; set; }

        [Required(ErrorMessage = "Выберите файлы для загрузки ")]
        [AllowedExtensions(new string[]{".jpg", ".png"},
            ErrorMessage ="Для загрузки допускаются только файлы формата jpg и png")]
        public IFormFileCollection Files { get; set; }
    }
}
