using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc.ModelBinding.Validation;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace DentaTest.Infrastructure
{
    public class AllowedExtensionsAttribute : ValidationAttribute
    {
        private readonly string[] extensions;

        public AllowedExtensionsAttribute(string[] ext)
        {
            extensions = ext;
        }

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            var files = value as IFormFileCollection;
            foreach (var file in files)
            {
                var fileExtension = Path.GetExtension(file.FileName);
                if (!extensions.Contains(fileExtension.ToLower()))
                {
                    return new ValidationResult(ErrorMessage);
                } 
            }
            return ValidationResult.Success;
        }
    }
}
