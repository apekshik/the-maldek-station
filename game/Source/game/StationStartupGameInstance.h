#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "Containers/Ticker.h"
#include "RenderCommandFence.h"
#include "StationStartupGameInstance.generated.h"

class SWidget;
class STextBlock;
class UGameViewportClient;
class UTexture2D;

/** Shared desktop startup. No map assets or platform-specific PSO caches are embedded. */
UCLASS(Config=Game)
class GAME_API UStationStartupGameInstance : public UGameInstance
{
 GENERATED_BODY()
public:
 virtual void Init() override;
 virtual void Shutdown() override;
 bool IsOpeningReady() const { return Phase == EPhase::Playing; }
 // Console-accessible equivalent of the button for unattended startup smoke tests.
 UFUNCTION(Exec) void StationBeginShift();
private:
 enum class EPhase : uint8 { Boot, Menu, Travel, Warming, Playing, Failed };
 EPhase Phase = EPhase::Boot;
 UPROPERTY(Config) FString StationMap = TEXT("/Game/MaldekRefinement/R12/Station_R12");
 // Consecutive submitted scene frames after queues drain; temporal-history heuristic, not a timer.
 UPROPERTY(Config) int32 WarmupFrames = 30;
 FTSTicker::FDelegateHandle TickHandle;
 FDelegateHandle PreLoadHandle, PostLoadHandle, DrawHandle, TravelFailureHandle;
 TWeakObjectPtr<UGameViewportClient> AttachedViewport;
 TWeakObjectPtr<APlayerController> HeldController;
 TSharedPtr<SWidget> Screen;
 TSharedPtr<STextBlock> Status;
 UPROPERTY(Transient) TArray<TObjectPtr<UTexture2D>> MenuCaptures;
 bool bStartRequested = false;
 int32 ReadyFrames = 0;
 FRenderCommandFence WarmupFence;
 double LoadStartedAt = 0;
 double LastDiagnosticAt = 0;
 bool TickStartup(float DeltaTime);
 void BeforeMap(const FString& MapName);
 void AfterMap(UWorld* World);
 void SceneDrawn();
 void ShowMenu();
 void ShowLoading();
 void AttachScreen(const TSharedRef<SWidget>& Widget);
 void RemoveScreen();
 void HoldInput();
 void ReleaseInput();
 void TravelFailed(UWorld* World, ETravelFailure::Type Type, const FString& Error);
};
