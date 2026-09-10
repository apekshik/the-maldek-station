#include "StationMigrationLibrary.h"
#include "Misc/App.h"
#include "AudioDevice.h"

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
#include "Landscape.h"
#include "LandscapeInfo.h"
#include "LandscapeEdit.h"
#include "LandscapeEditLayer.h"
#include "Engine/Texture2D.h"
#include "GameFramework/PlayerController.h"
#include "InputKeyEventArgs.h"
#include "Input/Events.h"
#include "InstancedFoliageActor.h"
#include "InstancedFoliage.h"
#include "FoliageType.h"
#include "Engine/Blueprint.h"
#include "Editor.h"
#include "LevelEditorViewport.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, StationMigrationTools)

TArray<FString> UStationMigrationLibrary::SetEditorRenderingSuppressed(bool bSuppressed)
{
    static TMap<FLevelEditorViewportClient*, bool> SavedRendering;
    static const FText OverrideName = FText::FromString(TEXT("R12 benchmark isolation"));
    TArray<FString> Report;
    if (!GEditor) return Report;
    int32 Index = 0;
    for (FLevelEditorViewportClient* Client : GEditor->GetLevelViewportClients())
    {
        if (!Client) continue;
        const bool WasRealtime = Client->IsRealtime();
        const bool WasRendering = Client->EngineShowFlags.Rendering;
        const FString PriorOverride = Client->GetRealtimeOverrideMessage().ToString();
        if (bSuppressed)
        {
            if (!SavedRendering.Contains(Client))
            {
                SavedRendering.Add(Client, WasRendering);
                Client->AddRealtimeOverride(false, OverrideName);
            }
            Client->EngineShowFlags.SetRendering(false);
        }
        else if (const bool* Previous = SavedRendering.Find(Client))
        {
            Client->EngineShowFlags.SetRendering(*Previous);
            Client->RemoveRealtimeOverride(OverrideName, false);
        }
        Report.Add(FString::Printf(TEXT("Viewport %d: realtime %d -> %d; rendering %d -> %d; prior override: %s"),
            Index++, WasRealtime, Client->IsRealtime(), WasRendering, Client->EngineShowFlags.Rendering, *PriorOverride));
        Client->Invalidate();
    }
    if (!bSuppressed) SavedRendering.Empty();
    return Report;
}

bool UStationMigrationLibrary::IsBlueprintUpToDate(UBlueprint* Blueprint)
{
    return Blueprint && Blueprint->IsUpToDate();
}

TMap<FString, FTransform> UStationMigrationLibrary::GetFoliageInstanceTransforms(AActor* Actor)
{
    TMap<FString, FTransform> Result;
    if (auto* Foliage = Cast<AInstancedFoliageActor>(Actor))
        Foliage->ForEachFoliageInfo([&](UFoliageType* Type, FFoliageInfo& Info)
        {
            for (int32 Index = 0; Index < Info.Instances.Num(); ++Index)
                Result.Add(Type->GetPathName() + TEXT("|") + FString::FromInt(Index), Info.Instances[Index].GetInstanceWorldTransform());
            return true;
        });
    return Result;
}

bool UStationMigrationLibrary::MoveR12FoliageInstance(AActor* Actor, const FString& TypePath,
    int32 Index, FVector ExpectedLocation, FVector NewLocation)
{
    auto* Foliage = Cast<AInstancedFoliageActor>(Actor);
    if (!Foliage || (!Foliage->GetOutermost()->GetName().StartsWith(TEXT("/Game/MaldekRefinement/R12/"))
        && Foliage->GetOutermost()->GetName() != TEXT("/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration"))
        || !Foliage->GetWorld() || Foliage->GetWorld()->WorldType != EWorldType::Editor) return false;
    bool bMoved = false;
    Foliage->ForEachFoliageInfo([&](UFoliageType* Type, FFoliageInfo& Info)
    {
        if (Type->GetPathName() != TypePath || !Info.Instances.IsValidIndex(Index)) return true;
        if (!Info.Instances[Index].Location.Equals(ExpectedLocation, 0.1)) return false;
        Foliage->Modify();
        TArray<int32> Indices{Index};
        Info.PreMoveInstances(Indices);
        Info.Instances[Index].Location = NewLocation;
        Info.PostMoveInstances(Indices, true);
        Foliage->MarkPackageDirty();
        bMoved = true;
        return false;
    });
    return bMoved;
}

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

bool UStationMigrationLibrary::SendPIEKey(FName KeyName, bool bPressed)
{
    auto* Client = FindPIEViewport();
    if (!Client || !Client->GetWorld()) return false;
    auto* Controller = Client->GetWorld()->GetFirstPlayerController();
    const FKey Key(KeyName);
    if (!Controller || !Key.IsValid()) return false;
    return Controller->InputKey(FInputKeyEventArgs(Client->Viewport,
        FInputDeviceId::CreateFromInternalId(0), Key, bPressed ? IE_Pressed : IE_Released,
        bPressed ? 1.0f : 0.0f, false, FPlatformTime::Cycles64()));
}

bool UStationMigrationLibrary::SendPIEMousePosition(float X, float Y)
{
    auto* Client=FindPIEViewport();
    if(!Client || !Client->Viewport || !FMath::IsFinite(X) || !FMath::IsFinite(Y))return false;
    auto* Viewport=static_cast<FSceneViewport*>(Client->Viewport);
    const FGeometry& Geometry=Viewport->GetCachedGeometry();
    const FIntPoint Size=Viewport->GetSizeXY();
    if(Size.X<=0 || Size.Y<=0)return false;
    // GetMousePos reads cached physical pixels even when PIE has a fixed render size.
    const FVector2D Local=FVector2D(X,Y)/Geometry.GetAccumulatedLayoutTransform().GetScale();
    const FVector2D Absolute=Geometry.LocalToAbsolute(Local);
    TSet<FKey> Pressed;
    if(auto* PC=Client->GetWorld()->GetFirstPlayerController())if(PC->IsInputKeyDown(EKeys::LeftMouseButton))Pressed.Add(EKeys::LeftMouseButton);
    const FPointerEvent Event(0,Absolute,Absolute,Pressed,EKeys::Invalid,0,FModifierKeysState());
    Viewport->OnMouseMove(Geometry,Event);return true;
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

namespace
{
bool ValidStationPatch(ALandscape* Land, int32 X1, int32 Y1, int32 X2, int32 Y2, int32 LayerIndex)
{
    if (!Land) return false;
    const FString MapPackage = Land->GetPackage()->GetName();
    const bool bAllowedMap = MapPackage == TEXT("/Game/MaldekRefinement/R12/Station_R12") ||
        MapPackage == TEXT("/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration");
    if (!bAllowedMap ||
        !Land->GetLandscapeInfo() || X2 < X1 || Y2 < Y1 ||
        int64(X2-X1+1)*int64(Y2-Y1+1) > 100000 || LayerIndex < -1) return false;
    int32 MinX, MinY, MaxX, MaxY;
    if (!Land->GetLandscapeInfo()->GetLandscapeExtent(MinX, MinY, MaxX, MaxY) ||
        X1 < MinX || Y1 < MinY || X2 > MaxX || Y2 > MaxY) return false;
    if (LayerIndex >= 0 && !Land->GetEditLayer(LayerIndex)) return false;
    for (const FString& Path : UStationMigrationLibrary::GetLandscapeHeightmapPaths(Land))
        if (!Path.StartsWith(MapPackage + TEXT("."))) return false;
    return true;
}
}

TArray<int32> UStationMigrationLibrary::ReadR12LandscapePatch(AActor* Actor, int32 X1, int32 Y1, int32 X2, int32 Y2, int32 LayerIndex)
{
    TArray<int32> Result;
    ALandscape* Land = Cast<ALandscape>(Actor);
    if (!ValidStationPatch(Land, X1, Y1, X2, Y2, LayerIndex)) return Result;
    const FGuid Guid = LayerIndex >= 0 ? Land->GetEditLayer(LayerIndex)->GetGuid() : FGuid();
    FLandscapeEditDataInterface Edit(Land->GetLandscapeInfo(), Guid);
    TArray<uint16> Values; Values.SetNumZeroed((X2-X1+1)*(Y2-Y1+1));
    Edit.GetHeightDataFast(X1,Y1,X2,Y2,Values.GetData(),0);
    for (uint16 Value : Values) Result.Add(Value);
    return Result;
}

FString UStationMigrationLibrary::ApplyR12LandscapePatch(AActor* Actor, int32 X1, int32 Y1, int32 X2, int32 Y2, int32 LayerIndex, const TArray<int32>& Expected, const TArray<int32>& Heights)
{
    ALandscape* Land = Cast<ALandscape>(Actor);
    if (!ValidStationPatch(Land,X1,Y1,X2,Y2,LayerIndex) || LayerIndex < 0) return TEXT("Rejected patch bounds, ownership or layer");
    const int32 Count = (X2-X1+1)*(Y2-Y1+1);
    if (Expected.Num()!=Count || Heights.Num()!=Count) return TEXT("Rejected array size");
    for (int32 H : Heights) if (H<0 || H>65535) return TEXT("Rejected height range");
    if (ReadR12LandscapePatch(Actor,X1,Y1,X2,Y2,LayerIndex)!=Expected) return TEXT("Rejected stale source heights");
    TArray<uint16> Data; Data.Reserve(Count);
    int32 Changed=0;
    for (int32 I=0;I<Count;++I) { Data.Add(uint16(Heights[I])); Changed += Heights[I]!=Expected[I]; }
    if (!Changed) return TEXT("OK unchanged");
    FScopedSetLandscapeEditingLayer Scope(Land,Land->GetEditLayer(LayerIndex)->GetGuid());
    FLandscapeEditDataInterface Edit(Land->GetLandscapeInfo());
    TSet<ULandscapeComponent*> Components;
    if (!Edit.GetComponentsInRegion(X1,Y1,X2,Y2,&Components)) return TEXT("Rejected missing components");
    Land->Modify();
    for (ULandscapeComponent* Component : Components) Component->Modify();
    Edit.SetHeightData(X1,Y1,X2,Y2,Data.GetData(),0,false);
    Edit.Flush();
    for (ULandscapeComponent* Component : Components) Component->RequestHeightmapUpdate();
    Land->MarkPackageDirty();
    return FString::Printf(TEXT("OK %d heights, %d components"),Changed,Components.Num());
}

TMap<FString,double> UStationMigrationLibrary::SetPIEAudioCaptureEnabled(bool bEnabled)
{
 static bool bOverridden=false;
 static float PriorUnfocused=0,PriorVolume=1;
 static TMap<uint32,bool> PriorMute;
 TMap<FString,double> Report;
 Report.Add(TEXT("VolumeBefore"),FApp::GetVolumeMultiplier());
 Report.Add(TEXT("UnfocusedBefore"),FApp::GetUnfocusedVolumeMultiplier());
 if(bEnabled&&!bOverridden)
 { PriorUnfocused=FApp::GetUnfocusedVolumeMultiplier(); PriorVolume=FApp::GetVolumeMultiplier(); bOverridden=true; }
 if(bEnabled) { FApp::SetUnfocusedVolumeMultiplier(1); FApp::SetVolumeMultiplier(1); }
 else if(bOverridden) { FApp::SetUnfocusedVolumeMultiplier(PriorUnfocused); FApp::SetVolumeMultiplier(PriorVolume); }
 if(GEngine)for(const FWorldContext& C:GEngine->GetWorldContexts())if(C.WorldType==EWorldType::PIE&&C.World())
 {
  auto Device=C.World()->GetAudioDevice();
  if(Device.IsValid())
  {
   const uint32 Id=Device.GetDeviceID();
   Report.Add(FString::Printf(TEXT("Device%uMutedBefore"),Id),Device->IsAudioDeviceMuted()?1:0);
   if(bEnabled) { if(!PriorMute.Contains(Id))PriorMute.Add(Id,Device->IsAudioDeviceMuted()); Device->SetDeviceMuted(false); }
   else if(const bool* Muted=PriorMute.Find(Id))Device->SetDeviceMuted(*Muted);
  }
 }
 if(!bEnabled) { bOverridden=false; PriorMute.Empty(); }
 return Report;
}
