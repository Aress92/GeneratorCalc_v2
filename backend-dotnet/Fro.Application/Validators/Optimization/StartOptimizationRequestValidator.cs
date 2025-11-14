using FluentValidation;
using Fro.Application.DTOs.Optimization;

namespace Fro.Application.Validators.Optimization;

/// <summary>
/// Validator for start optimization requests.
/// </summary>
public class StartOptimizationRequestValidator : AbstractValidator<StartOptimizationRequest>
{
    public StartOptimizationRequestValidator()
    {
        RuleFor(x => x.ScenarioId)
            .NotEmpty().WithMessage("Scenario ID is required");

        RuleFor(x => x.Priority)
            .GreaterThanOrEqualTo(0).WithMessage("Priority must be 0 or greater")
            .LessThanOrEqualTo(10).WithMessage("Priority cannot exceed 10");
    }
}
