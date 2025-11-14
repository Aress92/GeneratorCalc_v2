using FluentValidation;
using Fro.Application.DTOs.Users;

namespace Fro.Application.Validators.Users;

/// <summary>
/// Validator for user update requests.
/// </summary>
public class UpdateUserRequestValidator : AbstractValidator<UpdateUserRequest>
{
    public UpdateUserRequestValidator()
    {
        RuleFor(x => x.Email)
            .EmailAddress().WithMessage("Invalid email format")
            .MaximumLength(255).WithMessage("Email cannot exceed 255 characters")
            .When(x => !string.IsNullOrEmpty(x.Email));

        RuleFor(x => x.FullName)
            .MaximumLength(255).WithMessage("Full name cannot exceed 255 characters")
            .When(x => !string.IsNullOrEmpty(x.FullName));

        RuleFor(x => x.Role)
            .IsInEnum().WithMessage("Invalid role specified")
            .When(x => x.Role.HasValue);
    }
}
