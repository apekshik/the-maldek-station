using UnrealBuildTool;

public class StationMigrationTools : ModuleRules
{
    public StationMigrationTools(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new[] { "UnrealEd", "Slate", "SlateCore", "RHI", "RenderCore", "Landscape", "InputCore", "Foliage" });
    }
}
