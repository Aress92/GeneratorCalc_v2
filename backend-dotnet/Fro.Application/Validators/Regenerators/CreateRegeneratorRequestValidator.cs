using FluentValidation;
using Fro.Application.DTOs.Regenerators;

namespace Fro.Application.Validators.Regenerators;

/// <summary>
/// Validator for regenerator configuration creation requests.
/// </summary>
public class CreateRegeneratorRequestValidator : AbstractValidator<CreateRegeneratorRequest>
{
    public CreateRegeneratorRequestValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Configuration name is required")
            .MinimumLength(3).WithMessage("Name must be at least 3 characters")
            .MaximumLength(255).WithMessage("Name cannot exceed 255 characters");

        RuleFor(x => x.Description)
            .MaximumLength(2000).WithMessage("Description cannot exceed 2000 characters")
            .When(x => !string.IsNullOrEmpty(x.Description));

        RuleFor(x => x.RegeneratorType)
            .IsInEnum().WithMessage("Invalid regenerator type specified");
    }
}
