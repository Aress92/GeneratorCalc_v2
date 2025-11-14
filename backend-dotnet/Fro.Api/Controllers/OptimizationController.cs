using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Fro.Application.DTOs.Common;
using Fro.Application.DTOs.Optimization;
using Fro.Application.Interfaces.Services;

namespace Fro.Api.Controllers;

/// <summary>
/// Optimization scenario and job management controller.
/// </summary>
[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
[Authorize]
public class OptimizationController : ControllerBase
{
    private readonly IOptimizationService _optimizationService;
    private readonly ILogger<OptimizationController> _logger;

    public OptimizationController(
        IOptimizationService optimizationService,
        ILogger<OptimizationController> logger)
    {
        _optimizationService = optimizationService;
        _logger = logger;
    }

    /// <summary>
    /// Get current user ID from JWT token.
    /// </summary>
    private Guid GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst("sub")?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            throw new UnauthorizedAccessException("Invalid user token");
        }
        return userId;
    }

    /// <summary>
    /// Get paginated list of optimization scenarios for current user.
    /// </summary>
    /// <param name="request">Pagination and filtering parameters</param>
    /// <returns>Paginated list of scenarios</returns>
    /// <response code="200">Scenarios retrieved successfully</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet("scenarios")]
    [ProducesResponseType(typeof(PaginatedResponse<OptimizationScenarioDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<PaginatedResponse<OptimizationScenarioDto>>> GetScenarios(
        [FromQuery] OptimizationListRequest request)
    {
        try
        {
            var userId = GetCurrentUserId();
            var result = await _optimizationService.GetUserScenariosAsync(userId, request);
            return Ok(result);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Unauthorized(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving optimization scenarios");
            return StatusCode(500, new { message = "An error occurred while retrieving scenarios" });
        }
    }

    /// <summary>
    /// Get optimization scenario by ID.
    /// </summary>
    /// <param name="id">Scenario ID</param>
    /// <returns>Scenario details</returns>
    /// <response code="200">Scenario found</response>
    /// <response code="404">Scenario not found</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet("scenarios/{id}")]
    [ProducesResponseType(typeof(OptimizationScenarioDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<OptimizationScenarioDto>> GetScenarioById(Guid id)
    {
        try
        {
            var userId = GetCurrentUserId();
            var scenario = await _optimizationService.GetScenarioByIdAsync(id, userId);

            if (scenario == null)
            {
                return NotFound(new { message = "Scenario not found or access denied" });
            }

            return Ok(scenario);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Unauthorized(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving scenario {ScenarioId}", id);
            return StatusCode(500, new { message = "An error occurred while retrieving scenario" });
        }
    }

    /// <summary>
    /// Create new optimization scenario.
    /// </summary>
    /// <param name="request">Scenario creation data</param>
    /// <returns>Created scenario</returns>
    /// <response code="201">Scenario created successfully</response>
    /// <response code="400">Invalid data</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Access denied to base configuration</response>
    [HttpPost("scenarios")]
    [ProducesResponseType(typeof(OptimizationScenarioDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<OptimizationScenarioDto>> CreateScenario(
        [FromBody] CreateOptimizationScenarioRequest request)
    {
        try
        {
            var userId = GetCurrentUserId();
            var scenario = await _optimizationService.CreateScenarioAsync(request, userId);

            _logger.LogInformation("User {UserId} created optimization scenario {ScenarioId}",
                userId, scenario.Id);
            return CreatedAtAction(nameof(GetScenarioById), new { id = scenario.Id }, scenario);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(403, new { message = ex.Message });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating optimization scenario");
            return StatusCode(500, new { message = "An error occurred while creating scenario" });
        }
    }

    /// <summary>
    /// Start optimization job for a scenario.
    /// </summary>
    /// <param name="request">Optimization start request</param>
    /// <returns>Created job</returns>
    /// <response code="201">Optimization job started successfully</response>
    /// <response code="400">Invalid scenario or parameters</response>
    /// <response code="404">Scenario not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Access denied</response>
    [HttpPost("jobs/start")]
    [ProducesResponseType(typeof(OptimizationJobDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<OptimizationJobDto>> StartOptimization(
        [FromBody] StartOptimizationRequest request)
    {
        try
        {
            var userId = GetCurrentUserId();
            var job = await _optimizationService.StartOptimizationAsync(request, userId);

            _logger.LogInformation("User {UserId} started optimization job {JobId} for scenario {ScenarioId}",
                userId, job.Id, request.ScenarioId);
            return CreatedAtAction(nameof(GetJobById), new { id = job.Id }, job);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(403, new { message = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting optimization job");
            return StatusCode(500, new { message = "An error occurred while starting optimization" });
        }
    }

    /// <summary>
    /// Get optimization job by ID.
    /// </summary>
    /// <param name="id">Job ID</param>
    /// <returns>Job details</returns>
    /// <response code="200">Job found</response>
    /// <response code="404">Job not found</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet("jobs/{id}")]
    [ProducesResponseType(typeof(OptimizationJobDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<OptimizationJobDto>> GetJobById(Guid id)
    {
        try
        {
            var userId = GetCurrentUserId();
            var job = await _optimizationService.GetJobByIdAsync(id, userId);

            if (job == null)
            {
                return NotFound(new { message = "Job not found or access denied" });
            }

            return Ok(job);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Unauthorized(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving job {JobId}", id);
            return StatusCode(500, new { message = "An error occurred while retrieving job" });
        }
    }

    /// <summary>
    /// Get all jobs for a scenario.
    /// </summary>
    /// <param name="scenarioId">Scenario ID</param>
    /// <returns>List of jobs</returns>
    /// <response code="200">Jobs retrieved successfully</response>
    /// <response code="404">Scenario not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Access denied</response>
    [HttpGet("scenarios/{scenarioId}/jobs")]
    [ProducesResponseType(typeof(List<OptimizationJobDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<List<OptimizationJobDto>>> GetScenarioJobs(Guid scenarioId)
    {
        try
        {
            var userId = GetCurrentUserId();
            var jobs = await _optimizationService.GetScenarioJobsAsync(scenarioId, userId);
            return Ok(jobs);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(403, new { message = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving jobs for scenario {ScenarioId}", scenarioId);
            return StatusCode(500, new { message = "An error occurred while retrieving jobs" });
        }
    }

    /// <summary>
    /// Cancel running optimization job.
    /// </summary>
    /// <param name="id">Job ID</param>
    /// <returns>Success message</returns>
    /// <response code="200">Job cancelled successfully</response>
    /// <response code="404">Job not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Access denied</response>
    [HttpPost("jobs/{id}/cancel")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> CancelJob(Guid id)
    {
        try
        {
            var userId = GetCurrentUserId();
            await _optimizationService.CancelJobAsync(id, userId);

            _logger.LogInformation("User {UserId} cancelled optimization job {JobId}", userId, id);
            return Ok(new { message = "Optimization job cancelled successfully" });
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(403, new { message = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error cancelling job {JobId}", id);
            return StatusCode(500, new { message = "An error occurred while cancelling job" });
        }
    }

    /// <summary>
    /// Get job progress and status.
    /// </summary>
    /// <param name="id">Job ID</param>
    /// <returns>Job progress information</returns>
    /// <response code="200">Progress retrieved successfully</response>
    /// <response code="404">Job not found</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet("jobs/{id}/progress")]
    [ProducesResponseType(typeof(JobProgress), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<JobProgress>> GetJobProgress(Guid id)
    {
        try
        {
            var progress = await _optimizationService.GetJobProgressAsync(id);
            return Ok(progress);
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving job progress {JobId}", id);
            return StatusCode(500, new { message = "An error occurred while retrieving progress" });
        }
    }
}
