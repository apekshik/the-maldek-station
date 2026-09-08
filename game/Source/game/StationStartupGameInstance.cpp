#include "StationStartupGameInstance.h"
#include "ScenicMenuBackdrop.h"
#include "ImageUtils.h"
#include "Misc/Paths.h"
#include "Misc/PackageName.h"
#include "Widgets/SOverlay.h"
#include "ContentStreaming.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/LevelStreaming.h"
#include "Engine/StreamableRenderAsset.h"
#include "WorldPartition/WorldPartitionSubsystem.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "MoviePlayer.h"
#include "ShaderPipelineCache.h"
#include "UObject/UObjectGlobals.h"
#include "UObject/UObjectIterator.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Images/SThrobber.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"
#include "Framework/Application/SlateApplication.h"

DEFINE_LOG_CATEGORY_STATIC(LogStationStartup, Log, All);

namespace
{
 TSharedRef<STextBlock> Label(const TCHAR* Text, int32 Size, FLinearColor Color = FLinearColor(.78f,.79f,.75f))
 {
  return SNew(STextBlock).Text(FText::FromString(Text))
   .Font(FCoreStyle::GetDefaultFontStyle("Regular",Size)).ColorAndOpacity(Color);
 }
 TSharedRef<SWidget> Frame(const TSharedRef<SWidget>& Content)
 {
  return SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
   .BorderBackgroundColor(FLinearColor(.009f,.014f,.015f,1))
   .HAlign(HAlign_Center).VAlign(VAlign_Center).Padding(48)
   [SNew(SBox).WidthOverride(540)[Content]];
 }
 // Only Slate objects here: MoviePlayer may paint this while the game thread is blocked.
 TSharedRef<SWidget> TravelScreen()
 {
  return Frame(SNew(SVerticalBox)
   + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,16)[Label(TEXT("MALDEK STATION"),36)]
   + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,32)[Label(TEXT("Beyond the last light."),16)]
   + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Left).Padding(0,0,0,18)[SNew(SThrobber)]
   + SVerticalBox::Slot().AutoHeight()[Label(TEXT("Loading the station..."),16)]);
 }
}

void UStationStartupGameInstance::Init()
{
 Super::Init();
 if (IsRunningDedicatedServer() || IsRunningCommandlet()) { Phase=EPhase::Playing; return; }
 PreLoadHandle=FCoreUObjectDelegates::PreLoadMap.AddUObject(this,&ThisClass::BeforeMap);
 PostLoadHandle=FCoreUObjectDelegates::PostLoadMapWithWorld.AddUObject(this,&ThisClass::AfterMap);
 TravelFailureHandle=GEngine->OnTravelFailure().AddUObject(this,&ThisClass::TravelFailed);
 TickHandle=FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateUObject(this,&ThisClass::TickStartup));
}

void UStationStartupGameInstance::BeforeMap(const FString& MapName)
{
 if (GetWorld() && GetWorld()->WorldType==EWorldType::PIE) return;
 FShaderPipelineCache::SetBatchMode(FShaderPipelineCache::BatchMode::Fast);
 if (IsMoviePlayerEnabled())
 {
  FLoadingScreenAttributes Attributes;
  Attributes.bMoviesAreSkippable=false;
  Attributes.WidgetLoadingScreen=TravelScreen();
  GetMoviePlayer()->SetupLoadingScreen(Attributes);
 }
}

void UStationStartupGameInstance::AfterMap(UWorld* World)
{
 if (!World || World->GetGameInstance()!=this) return;
 // Editor play retains its direct-to-map iteration workflow.
 if (World->WorldType==EWorldType::PIE) { Phase=EPhase::Playing; return; }
 if (World->GetPackage()->GetName()==StationMap)
 {
  Phase=EPhase::Warming;
  ReadyFrames=0;
  if (LoadStartedAt==0) LoadStartedAt=FPlatformTime::Seconds();
  ShowLoading();
  UE_LOG(LogStationStartup,Log,TEXT("Map loaded; waiting for BeginPlay, PSOs, streaming and scene frames."));
 }
}

void UStationStartupGameInstance::AttachScreen(const TSharedRef<SWidget>& Widget)
{
 RemoveScreen();
 if (UGameViewportClient* Viewport=GetGameViewportClient())
 {
  Screen=Widget;
  AttachedViewport=Viewport;
  Viewport->AddViewportWidgetContent(Widget,10000);
  DrawHandle=Viewport->OnEndDraw().AddUObject(this,&ThisClass::SceneDrawn);
 }
}

void UStationStartupGameInstance::RemoveScreen()
{
 if (UGameViewportClient* Viewport=AttachedViewport.Get())
 {
  if (Screen) Viewport->RemoveViewportWidgetContent(Screen.ToSharedRef());
  Viewport->OnEndDraw().Remove(DrawHandle);
 }
 Screen.Reset(); Status.Reset(); AttachedViewport.Reset();
}

void UStationStartupGameInstance::ShowMenu()
{
 Phase=EPhase::Menu;
 FShaderPipelineCache::SetBatchMode(FShaderPipelineCache::BatchMode::Background);
 if (MenuCaptures.IsEmpty())
 {
  for (const TCHAR* File : {TEXT("approach.png"),TEXT("parking.png"),TEXT("cables.png")})
  {
   const FString Path=FPaths::Combine(FPaths::ProjectContentDir(),TEXT("UI/Menu"),File);
   if (UTexture2D* Texture=FImageUtils::ImportFileAsTexture2D(Path)) MenuCaptures.Add(Texture);
   else UE_LOG(LogStationStartup,Warning,TEXT("Menu capture unavailable: %s"),*Path);
  }
  UE_LOG(LogStationStartup,Log,TEXT("Loaded %d scenic menu captures."),MenuCaptures.Num());
 }
 TSharedPtr<SButton> StartButton;
 auto MenuContent=SNew(SVerticalBox)
  + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,18)[Label(TEXT("MALDEK STATION"),40)]
  + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,56)[Label(TEXT("Beyond the last light."),18)]
  + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,14)
  [SAssignNew(StartButton,SButton).ContentPadding(FMargin(22,14)).ButtonColorAndOpacity(FLinearColor(.07f,.12f,.11f))
   .OnClicked_Lambda([this](){ StationBeginShift(); return FReply::Handled(); })[Label(TEXT("Begin shift"),20)]]
  + SVerticalBox::Slot().AutoHeight()
  [SNew(SButton).ContentPadding(FMargin(22,14)).ButtonColorAndOpacity(FLinearColor(.04f,.06f,.06f))
   .OnClicked_Lambda([](){ FPlatformMisc::RequestExit(false); return FReply::Handled(); })[Label(TEXT("Quit"),18)]];
 auto Menu=SNew(SOverlay)
  + SOverlay::Slot()[SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
    .BorderBackgroundColor(FLinearColor(.009f,.014f,.015f,1))]
  + SOverlay::Slot()[SNew(SScenicMenuBackdrop,MenuCaptures)]
  + SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Center).Padding(FMargin(72,48))
   [SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
    .BorderBackgroundColor(FLinearColor(0,0,0,.48f)).Padding(32)
    [SNew(SBox).WidthOverride(480)[MenuContent]]];
 AttachScreen(Menu);
 HoldInput();
 if (APlayerController* PC=GetFirstLocalPlayerController())
 {
  FInputModeUIOnly Mode; Mode.SetWidgetToFocus(StartButton); PC->SetInputMode(Mode);
 }
 FSlateApplication::Get().SetKeyboardFocus(StartButton);
 UE_LOG(LogStationStartup,Log,TEXT("Title menu ready."));
}

void UStationStartupGameInstance::ShowLoading()
{
 // AttachScreen clears Status, so retain a local pointer until attachment is complete.
 TSharedPtr<STextBlock> NewStatus;
 auto Loading=Frame(SNew(SVerticalBox)
  + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,16)[Label(TEXT("MALDEK STATION"),36)]
  + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,32)[Label(TEXT("Beyond the last light."),16)]
  + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Left).Padding(0,0,0,18)
  [SNew(SThrobber).Visibility(Phase==EPhase::Failed?EVisibility::Collapsed:EVisibility::Visible)]
  + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,32)
  [SAssignNew(NewStatus,STextBlock).Text(FText::FromString(TEXT("Preparing the station...")))
   .Font(FCoreStyle::GetDefaultFontStyle("Regular",16)).ColorAndOpacity(FLinearColor(.78f,.79f,.75f)).AutoWrapText(true)]
  + SVerticalBox::Slot().AutoHeight()
  [SNew(SButton).ContentPadding(FMargin(18,10)).ButtonColorAndOpacity(FLinearColor(.04f,.06f,.06f))
   .OnClicked_Lambda([](){ FPlatformMisc::RequestExit(false); return FReply::Handled(); })[Label(TEXT("Quit"),16)]]);
 AttachScreen(Loading); Status=NewStatus;
 HoldInput();
}

void UStationStartupGameInstance::HoldInput()
{
 APlayerController* PC=GetFirstLocalPlayerController();
 if (!PC || HeldController==PC) return;
 ReleaseInput(); HeldController=PC;
 PC->SetIgnoreMoveInput(true); PC->SetIgnoreLookInput(true);
 PC->bShowMouseCursor=true; PC->SetInputMode(FInputModeUIOnly());
}

void UStationStartupGameInstance::ReleaseInput()
{
 if (APlayerController* PC=HeldController.Get())
 {
  PC->SetIgnoreMoveInput(false); PC->SetIgnoreLookInput(false);
  PC->bShowMouseCursor=false; PC->SetInputMode(FInputModeGameOnly());
 }
 HeldController.Reset();
}

bool UStationStartupGameInstance::TickStartup(float DeltaTime)
{
 UWorld* World=GetWorld();
 if (!World || !GetGameViewportClient()) return true;
 if (World->WorldType==EWorldType::PIE) { Phase=EPhase::Playing; return true; }
 if (Phase==EPhase::Boot && World->HasBegunPlay() && GetFirstLocalPlayerController()) ShowMenu();
 if (bStartRequested && Phase==EPhase::Menu)
 {
  bStartRequested=false; Phase=EPhase::Travel; LoadStartedAt=FPlatformTime::Seconds();
  UE_LOG(LogStationStartup,Log,TEXT("Begin shift requested: %s"),*StationMap);
  ShowLoading();
  if (FPackageName::DoesPackageExist(StationMap)) UGameplayStatics::OpenLevel(this,FName(*StationMap));
  else TravelFailed(World,ETravelFailure::PackageMissing,FString::Printf(TEXT("Missing station map: %s"),*StationMap));
 }
 if (Phase==EPhase::Warming)
 {
  if (!Screen) ShowLoading();
  HoldInput();
  if (Status && FPlatformTime::Seconds()-LoadStartedAt>90)
   Status->SetText(FText::FromString(TEXT("Preparation is taking longer than usual. Still working; you can wait or quit.")));
  if (ReadyFrames>=FMath::Max(1,WarmupFrames) && WarmupFence.IsFenceComplete())
  {
   // Change Slate ownership on the next tick, outside the viewport draw delegate.
   FShaderPipelineCache::SetBatchMode(FShaderPipelineCache::BatchMode::Background);
   Phase=EPhase::Playing; ReleaseInput(); RemoveScreen();
   UE_LOG(LogStationStartup,Log,TEXT("Ready after %.1fs; opening released."),FPlatformTime::Seconds()-LoadStartedAt);
  }
 }
 return true;
}

void UStationStartupGameInstance::StationBeginShift()
{
 if (Phase==EPhase::Menu || Phase==EPhase::Boot) bStartRequested=true;
}

void UStationStartupGameInstance::SceneDrawn()
{
 if (Phase!=EPhase::Warming) return;
 UWorld* World=GetWorld();
 APlayerController* PC=GetFirstLocalPlayerController();
 const int32 PSOs=FShaderPipelineCache::NumPrecompilesRemaining();
 auto& Streaming=IStreamingManager::Get();
 const int32 Wanted=Streaming.GetNumWantingResources();
 int32 PendingAssets=0;
 for (TObjectIterator<UStreamableRenderAsset> Asset;Asset;++Asset)
 {
  if (!Asset->IsTemplate() && Asset->HasPendingInitOrStreaming()) ++PendingAssets;
 }
 bool bLevelsReady=true;
 for (ULevelStreaming* Level:World->GetStreamingLevels())
  if (Level && Level->ShouldBeVisible() && !Level->IsLevelVisible()) bLevelsReady=false;
 if (UWorldPartitionSubsystem* Partition=World->GetSubsystem<UWorldPartitionSubsystem>())
  bLevelsReady &= Partition->IsAllStreamingCompleted();
 // The refresh-ID API does not advance on the tested UE 5.7 packaged path.
 // Observe real pending texture/mesh work instead. Consecutive rendered frames
 // allow the initial view to generate demand before we remove the cover.
 const bool bReady=World->HasBegunPlay() && PC && PC->GetPawn() && PC->PlayerCameraManager &&
  !IsAsyncLoading() && bLevelsReady && PSOs==0 && Wanted==0 && PendingAssets==0 &&
  AttachedViewport.IsValid() && !AttachedViewport->bDisableWorldRendering;
 ReadyFrames=bReady?ReadyFrames+1:0;
 if (ReadyFrames==FMath::Max(1,WarmupFrames)) WarmupFence.BeginFence();
 const double Now=FPlatformTime::Seconds();
 if (Now-LastDiagnosticAt>=5)
 {
  LastDiagnosticAt=Now;
  UE_LOG(LogStationStartup,Log,TEXT("Readiness: PSOs=%d wantedResources=%d pendingAssets=%d levels=%d warmFrames=%d elapsed=%.1fs"),
   PSOs,Wanted,PendingAssets,bLevelsReady,ReadyFrames,Now-LoadStartedAt);
 }
}

void UStationStartupGameInstance::TravelFailed(UWorld* World,ETravelFailure::Type Type,const FString& Error)
{
 if (World && World->GetGameInstance()!=this) return;
 Phase=EPhase::Failed; ShowLoading();
 if (Status) Status->SetText(FText::FromString(TEXT("The station could not be loaded. Please quit and verify your game installation.")));
 UE_LOG(LogStationStartup,Error,TEXT("Travel failed: %s"),*Error);
}

void UStationStartupGameInstance::Shutdown()
{
 FTSTicker::GetCoreTicker().RemoveTicker(TickHandle);
 FCoreUObjectDelegates::PreLoadMap.Remove(PreLoadHandle);
 FCoreUObjectDelegates::PostLoadMapWithWorld.Remove(PostLoadHandle);
 if (GEngine) GEngine->OnTravelFailure().Remove(TravelFailureHandle);
 ReleaseInput(); RemoveScreen();
 Super::Shutdown();
}
