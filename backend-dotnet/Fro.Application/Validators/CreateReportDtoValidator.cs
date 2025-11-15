using FluentValidation;
using Fro.Application.DTOs.Reports;

namespace Fro.Application.Validators;

/// <summary>
/// Validator for CreateReportDto.
/// </summary>
public class CreateReportDtoValidator : AbstractValidator<CreateReportDto>
{
    public CreateReportDtoValidator()
    {
        RuleFor(x => x.Title)
            .NotEmpty().WithMessage("Report title is required")
            .MaximumLength(255).WithMessage("Title must not exceed 255 characters");

        RuleFor(x => x.Description)
            .MaximumLength(2000).WithMessage("Description must not exceed 2000 characters")
            .When(x => x.Description != null);

        RuleFor(x => x.ReportType)
            .NotEmpty().WithMessage("Report type is required")
            .Must(BeValidReportType).WithMessage("Invalid report type");

        RuleFor(x => x.ReportConfig)
            .NotEmpty().WithMessage("Report configuration is required")
            .Must(BeValidJson).WithMessage("Report configuration must be valid JSON");

        RuleFor(x => x.DateRange)
            .Must(BeValidJson).WithMessage("Date range must be valid JSON")
            .When(x => x.DateRange != null);

        RuleFor(x => x.Filters)
            .Must(BeValidJson).WithMessage("Filters must be valid JSON")
            .When(x => x.Filters != null);

        RuleFor(x => x.Format)
            .Must(BeValidFormat).WithMessage("Invalid format. Valid formats: pdf, excel, csv, json, html");

        RuleFor(x => x.Frequency)
            .Must(BeValidFrequency).WithMessage("Invalid frequency. Valid frequencies: on_demand, daily, weekly, monthly, quarterly, annually");
    }

    private static bool BeValidReportType(string reportType)
    {
        var validTypes = new[]
        {
            "optimization_summary", "fuel_savings", "technical_metrics",
            "system_performance", "user_activity", "environmental_impact",
            "financial_analysis", "comparative_analysis", "custom"
        };
        return validTypes.Contains(reportType.ToLowerInvariant());
    }

    private static bool BeValidFormat(string format)
    {
        var validFormats = new[] { "pdf", "excel", "csv", "json", "html" };
        return validFormats.Contains(format.ToLowerInvariant());
    }

    private static bool BeValidFrequency(string frequency)
    {
        var validFrequencies = new[] { "on_demand", "daily", "weekly", "monthly", "quarterly", "annually" };
        return validFrequencies.Contains(frequency.ToLowerInvariant());
    }

    private static bool BeValidJson(string json)
    {
        if (string.IsNullOrWhiteSpace(json))
            return false;

        try
        {
            System.Text.Json.JsonDocument.Parse(json);
            return true;
        }
        catch
        {
            return false;
        }
    }
}
