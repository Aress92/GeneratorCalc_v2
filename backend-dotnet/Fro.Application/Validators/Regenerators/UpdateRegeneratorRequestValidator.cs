using FluentValidation;
using Fro.Application.DTOs.Regenerators;

namespace Fro.Application.Validators.Regenerators;

/// <summary>
/// Validator for regenerator configuration update requests.
/// </summary>
public class UpdateRegeneratorRequestValidator : AbstractValidator<UpdateRegeneratorRequest>
{
    public UpdateRegeneratorRequestValidator()
    {
        RuleFor(x => x.Name)
            .MinimumLength(3).WithMessage("Name must be at least 3 characters")
            .MaximumLength(255).WithMessage("Name cannot exceed 255 characters")
            .When(x => !string.IsNullOrEmpty(x.Name));

        RuleFor(x => x.Description)
            .MaximumLength(2000).WithMessage("Description cannot exceed 2000 characters")
            .When(x => !string.IsNullOrEmpty(x.Description));

        RuleFor(x => x.Status)
            .IsInEnum().WithMessage("Invalid status specified")
            .When(x => x.Status.HasValue);
    }
}
