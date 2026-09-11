#include "StationOpeningComponent.h"
#include "StationStartupGameInstance.h"
#include "UI/StationOpeningWidget.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Components/AudioComponent.h"

UStationOpeningComponent::UStationOpeningComponent(){PrimaryComponentTick.bCanEverTick=true;}
void UStationOpeningComponent::ReleaseInput()
{
 if(bInputHeld && Controller){Controller->SetIgnoreMoveInput(false);Controller->SetIgnoreLookInput(false);}
 bInputHeld=false;
}
void UStationOpeningComponent::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* Function)
{
 Super::TickComponent(Dt,TickType,Function);
 if(!bEnableOpening)return;
 if(const UStationStartupGameInstance* Startup=Cast<UStationStartupGameInstance>(GetWorld()->GetGameInstance()))
  if(!Startup->IsOpeningReady())return;
 if(!bStarted)
 {
  APawn* Pawn=Cast<APawn>(GetOwner());
  Controller=Pawn?Cast<APlayerController>(Pawn->GetController()):nullptr;
  if(!Controller || !Controller->IsLocalController())return;
  bStarted=true;
  UE_LOG(LogTemp,Log,TEXT("Station opening started (elapsed=%.3f)."),Elapsed);
  Widget=CreateWidget<UStationOpeningWidget>(Controller);
  if(Widget){Widget->SetVisibility(ESlateVisibility::HitTestInvisible);Widget->AddToPlayerScreen(100);}
  // Gameplay begins immediately; this component only supplies audio and hints.
  if(OpeningAtmosphere)Atmosphere=UGameplayStatics::SpawnSound2D(this,OpeningAtmosphere,AtmosphereVolume,1,0,nullptr,false,true);
 }
 Elapsed+=Dt;
 // A single approach transition per play session, so backing across the boundary
 // never restarts the drone or stacks additional music voices.
 if(StationAtmosphere && StationAtmosphereStartCount==0 &&
    FVector::DistSquared(GetOwner()->GetActorLocation(),StationApproachLocation)<=FMath::Square(StationApproachRadius))
 {
  StationAudio=UGameplayStatics::CreateSound2D(this,StationAtmosphere,StationAtmosphereVolume,1,0,nullptr,false,true);
  if(StationAudio)
  {
   StationAudio->FadeIn(5.f,StationAtmosphereVolume);
   if(Atmosphere && Atmosphere->IsPlaying())Atmosphere->FadeOut(5.f,0.f);
   ++StationAtmosphereStartCount;
   StationStartedAt=Elapsed;
  }
 }
 if(StationAudio && !bStationFading && Elapsed-StationStartedAt>=StationAtmosphereHoldSeconds)
 {
  StationAudio->FadeOut(12.f,0.f);bStationFading=true;
 }
 if(Widget)
 {
  Widget->Elapsed=Elapsed;Widget->bToggled=bTriedToggle;Widget->bFocused=bTriedFocus;
  if(bTriedToggle && bTriedFocus)Widget->HintEnd=FMath::Min(Widget->HintEnd,FMath::Max(17.0f,Elapsed+2.0f));
  Widget->InvalidateLayoutAndVolatility();
  if(Elapsed>=Widget->HintEnd){Widget->RemoveFromParent();Widget=nullptr;}
 }
}
void UStationOpeningComponent::FlashlightToggled(bool bEnabled)
{
 APawn* Pawn=Cast<APawn>(GetOwner());if(!Pawn || !Pawn->IsLocallyControlled())return;
 if(USoundBase* Sound=bEnabled?SwitchOn.Get():SwitchOff.Get())
 {UGameplayStatics::PlaySound2D(this,Sound,SwitchVolume);++SwitchCount;}
 if(Elapsed>=11.0f)bTriedToggle=true;
}
void UStationOpeningComponent::FocusAdjusted(){if(Elapsed>=11.0f)bTriedFocus=true;}
bool UStationOpeningComponent::IsStationAtmospherePlaying() const{return StationAudio && StationAudio->IsPlaying();}
void UStationOpeningComponent::EndPlay(const EEndPlayReason::Type Reason)
{
 ReleaseInput();if(Widget)Widget->RemoveFromParent();if(Atmosphere)Atmosphere->Stop();if(StationAudio)StationAudio->Stop();
 Super::EndPlay(Reason);
}
