using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.DependencyInjection;
using Orleans;
using Orleans.Configuration;
using Orleans.Hosting;
using Orleans.Serialization;
using AutonomousValidation.Orleans.Grains;
using AutonomousValidation.Orleans.Interfaces;
using AutonomousValidation.Core.Models;

namespace AutonomousValidation.Orleans;

class Program
{
    public static async Task<int> Main(string[] args)
    {
        try
        {
            // Force assembly loading for grain discovery
            var grainAssembly = typeof(ModelManagerGrain).Assembly;
            var interfaceAssembly = typeof(IModelManagerGrain).Assembly;
            Console.WriteLine($"Loaded grain assembly: {grainAssembly.GetName().Name}");
            Console.WriteLine($"Loaded interface assembly: {interfaceAssembly.GetName().Name}");
            
            var builder = WebApplication.CreateBuilder(args);

            // Add Orleans to the host
            builder.Host.UseOrleans((context, siloBuilder) =>
            {
                siloBuilder
                    .UseLocalhostClustering()
                    .ConfigureLogging(logging => logging.AddConsole())
                    .UseInMemoryReminderService()
                    .AddMemoryGrainStorageAsDefault()
                    .AddMemoryGrainStorage("PubSubStore")
                    .UseDashboard(options => 
                    {
                        options.Host = "*";
                        options.Port = 8080;
                        options.HostSelf = false; // Let ASP.NET Core handle the hosting
                    });
                    
                // Configure memory thresholds from environment
                var maxMemoryGB = Environment.GetEnvironmentVariable("MAX_MEMORY_GB");
                if (maxMemoryGB != null)
                {
                    Console.WriteLine($"Configured max memory: {maxMemoryGB}GB");
                }
            });

            // Add services to the container
            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new Microsoft.OpenApi.Models.OpenApiInfo
                {
                    Title = "Autonomous Validation API",
                    Version = "v1",
                    Description = "API for managing ONNX models and running inference in Orleans"
                });
            });

            // Add CORS for development
            builder.Services.AddCors(options =>
            {
                options.AddDefaultPolicy(policy =>
                {
                    policy.AllowAnyOrigin()
                          .AllowAnyMethod()
                          .AllowAnyHeader();
                });
            });

            // Health checks
            builder.Services.AddHealthChecks();

            var app = builder.Build();

            // Configure the HTTP request pipeline
            if (app.Environment.IsDevelopment())
            {
                app.UseSwagger();
                app.UseSwaggerUI(c =>
                {
                    c.SwaggerEndpoint("/swagger/v1/swagger.json", "Autonomous Validation API v1");
                    c.RoutePrefix = "swagger";
                });
            }

            app.UseCors();
            app.UseRouting();
            app.UseAuthorization();

            // Map API controllers
            app.MapControllers();

            // Map health checks
            app.MapHealthChecks("/health");

            // Root endpoint
            app.MapGet("/", () => new
            {
                service = "Autonomous Validation Orleans",
                status = "running",
                endpoints = new
                {
                    api = "/api",
                    swagger = "/swagger",
                    health = "/health",
                    models = "/api/models",
                    orleans_dashboard = "/dashboard"
                },
                timestamp = DateTime.UtcNow
            });

            Console.WriteLine("Starting Orleans Silo and Web API...");
            await app.RunAsync();
            
            return 0;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed to start application: {ex}");
            return 1;
        }
    }
}
