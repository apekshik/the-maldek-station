#include "StationMigrationLibrary.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "HAL/PlatformMemory.h"
#include "Modules/ModuleManager.h"
#include "RHIStats.h"
#include "DynamicRHI.h"
#include "Slate/SceneViewport.h"
#include "UnrealClient.h"
#include "Materials/Material.h"
#include "Materials/MaterialInterface.h"
#include "MaterialShared.h"
#include "ShaderCompiler.h"
#include "LandscapeComponent.h"
#include "Engine/Texture2D.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, StationMigrationTools)

namespace
{
UGameViewportClient* FindPIEViewport()
{
    if (!GEngine) return nullptr;
    for (const FWorldContext& Context : GEngine->GetWorldContexts())
        if (Context.WorldType == EWorldType::PIE && Context.World())
            if (auto* Client = Context.World()->GetGameViewport()) return Client;
    return nullptr;
}
}

bool UStationMigrationLibrary::SetPIERenderSize(int32 Width, int32 Height)
{
    if (Width < 0 || Height < 0 || Width > 8192 || Height > 8192) return false;
    auto* Client = FindPIEViewport();
    if (!Client || !Client->Viewport) return false;
    static_cast<FSceneViewport*>(Client->Viewport)->SetFixedViewportSize(Width, Height);
    return true;
}

TMap<FString, double> UStationMigrationLibrary::CapturePIEFrameStats()
{
    TMap<FString, double> Result;
    auto* Client = FindPIEViewport();
    if (!Client || !Client->Viewport) return Result;
    const FIntPoint Size = Client->Viewport->GetSizeXY();
    Result.Add(TEXT("width"), Size.X);
    Result.Add(TEXT("height"), Size.Y);
    Result.Add(TEXT("process_physical_bytes"), static_cast<double>(FPlatformMemory::GetStats().UsedPhysical));
    Result.Add(TEXT("draw_calls"), GNumDrawCallsRHI[0]);
    if (const FStatUnitData* Unit = Client->GetStatUnitData())
    {
        Result.Add(TEXT("frame_ms"), Unit->RawFrameTime);
        Result.Add(TEXT("game_ms"), Unit->RawGameThreadTime);
        Result.Add(TEXT("render_ms"), Unit->RawRenderThreadTime);
        Result.Add(TEXT("rhi_ms"), Unit->RawRHITTime);
        Result.Add(TEXT("gpu_ms"), Unit->RawGPUFrameTime[0]);
        // FStatUnitData's optional memory counter is not initialized on every RHI.
        // Query texture residency explicitly instead of publishing an invalid total.
        static FTextureMemoryStats Memory;
        static double LastMemorySample = -1.0;
        const double Now = FPlatformTime::Seconds();
        if (Now - LastMemorySample >= 1.0)
        {
            RHIGetTextureMemoryStats(Memory);
            LastMemorySample = Now;
        }
        Result.Add(TEXT("streaming_texture_bytes"), static_cast<double>(Memory.StreamingMemorySize));
        Result.Add(TEXT("nonstreaming_texture_bytes"), static_cast<double>(Memory.NonStreamingMemorySize));
        Result.Add(TEXT("texture_pool_bytes"), static_cast<double>(Memory.TexturePoolSize));
        Result.Add(TEXT("dedicated_vram_bytes"), static_cast<double>(Memory.DedicatedVideoMemory));
    }
    return Result;
}

TArray<FString> UStationMigrationLibrary::ValidateMaterialShaders(const TArray<UMaterialInterface*>& Materials)
{
    if (GShaderCompilingManager) GShaderCompilingManager->FinishAllCompilation();
    TArray<FString> Errors;
    for (UMaterialInterface* Material : Materials)
    {
        if (!Material) { Errors.Add(TEXT("Missing material")); continue; }
        FMaterialResource* Resource = Material->GetMaterialResource(GMaxRHIShaderPlatform);
        if (!Resource && Material->GetMaterial())
            Resource = Material->GetMaterial()->GetMaterialResource(GMaxRHIShaderPlatform);
        if (!Resource) { Errors.Add(Material->GetPathName() + TEXT(": no shader resource")); continue; }
        for (const FString& Error : Resource->GetCompileErrors())
            Errors.Add(Material->GetPathName() + TEXT(": ") + Error);
    }
    return Errors;
}

TArray<FString> UStationMigrationLibrary::GetLandscapeHeightmapPaths(AActor* LandscapeActor)
{
    TArray<FString> Paths;
    if (!LandscapeActor) return Paths;
    TInlineComponentArray<ULandscapeComponent*> Components(LandscapeActor);
    for (ULandscapeComponent* Component : Components)
    {
        if (UTexture2D* Texture = Component->GetHeightmap(false)) Paths.AddUnique(Texture->GetPathName());
        if (UTexture2D* Texture = Component->GetHeightmap(true)) Paths.AddUnique(Texture->GetPathName());
    }
    return Paths;
}
