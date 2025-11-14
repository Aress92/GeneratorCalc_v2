using FluentValidation;
using Fro.Application.DTOs.Optimization;

namespace Fro.Application.Validators.Optimization;

/// <summary>
/// Validator for optimization scenario creation requests.
/// </summary>
public class CreateOptimizationScenarioRequestValidator : AbstractValidator<CreateOptimizationScenarioRequest>
{
    public CreateOptimizationScenarioRequestValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Scenario name is required")
            .MinimumLength(3).WithMessage("Name must be at least 3 characters")
            .MaximumLength(255).WithMessage("Name cannot exceed 255 characters");

        RuleFor(x => x.Description)
            .MaximumLength(2000).WithMessage("Description cannot exceed 2000 characters")
            .When(x => !string.IsNullOrEmpty(x.Description));

        RuleFor(x => x.BaseConfigurationId)
            .NotEmpty().WithMessage("Base configuration ID is required");

        RuleFor(x => x.Algorithm)
            .IsInEnum().WithMessage("Invalid optimization algorithm specified");

        RuleFor(x => x.MaxIterations)
            .GreaterThan(0).WithMessage("Max iterations must be greater than 0")
            .LessThanOrEqualTo(100000).WithMessage("Max iterations cannot exceed 100,000");

        RuleFor(x => x.MaxFunctionEvaluations)
            .GreaterThan(0).WithMessage("Max function evaluations must be greater than 0")
            .LessThanOrEqualTo(1000000).WithMessage("Max function evaluations cannot exceed 1,000,000");

        RuleFor(x => x.Tolerance)
            .GreaterThan(0).WithMessage("Tolerance must be greater than 0")
            .LessThanOrEqualTo(1.0).WithMessage("Tolerance cannot exceed 1.0");

        RuleFor(x => x.MaxRuntimeMinutes)
            .GreaterThan(0).WithMessage("Max runtime must be greater than 0")
            .LessThanOrEqualTo(1440).WithMessage("Max runtime cannot exceed 24 hours (1440 minutes)");

        RuleFor(x => x.OptimizationConfig)
            .NotEmpty().WithMessage("Optimization configuration is required")
            .Must(BeValidJson).WithMessage("Optimization configuration must be valid JSON");

        RuleFor(x => x.DesignVariables)
            .NotEmpty().WithMessage("Design variables are required")
            .Must(BeValidJson).WithMessage("Design variables must be valid JSON");

        RuleFor(x => x.ConstraintsConfig)
            .Must(BeValidJson).WithMessage("Constraints configuration must be valid JSON")
            .When(x => !string.IsNullOrEmpty(x.ConstraintsConfig));

        RuleFor(x => x.BoundsConfig)
            .Must(BeValidJson).WithMessage("Bounds configuration must be valid JSON")
            .When(x => !string.IsNullOrEmpty(x.BoundsConfig));
    }

    private bool BeValidJson(string? json)
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
