#include "StationDoor.h"
#include "Components/AudioComponent.h"
#include "Components/WidgetComponent.h"
#include "Sound/SoundBase.h"
#include "TimerManager.h"
#include "Engine/GameViewportClient.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "StationInteractionStyle.h"
#include "Styling/CoreStyle.h"
#include "Camera/CameraComponent.h"
#include "Components/MeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "InputCoreTypes.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/ConstructorHelpers.h"

AStationDoor::AStationDoor()
{
 PrimaryActorTick.bCanEverTick=true;
 DoorRoot=CreateDefaultSubobject<USceneComponent>(TEXT("DoorRoot"));RootComponent=DoorRoot;
 Hinge=CreateDefaultSubobject<USceneComponent>(TEXT("Hinge"));Hinge->SetupAttachment(DoorRoot);
 auto Mesh=[this](const TCHAR* Name,USceneComponent* Parent)
 {
  UStaticMeshComponent* C=CreateDefaultSubobject<UStaticMeshComponent>(Name);
  C->SetupAttachment(Parent);C->SetMobility(EComponentMobility::Movable);
  C->SetCollisionEnabled(ECollisionEnabled::NoCollision);return C;
 };
 Leaf=Mesh(TEXT("Leaf"),Hinge);Glass=Mesh(TEXT("Glass"),Hinge);
 FixedHardware=Mesh(TEXT("FixedHardware"),DoorRoot);Keypad=Mesh(TEXT("Keypad"),Hinge);
 InteriorElectronics=Mesh(TEXT("InteriorElectronics"),Hinge);ElectronicStrike=Mesh(TEXT("ElectronicStrike"),DoorRoot);
 LeafCollision=CreateDefaultSubobject<UBoxComponent>(TEXT("LeafCollision"));LeafCollision->SetupAttachment(Hinge);
 LeafCollision->SetRelativeLocation(FVector(64.6,-3.5,121.4));LeafCollision->SetBoxExtent(FVector(64.4,2.25,118.0));
 LeafCollision->SetCollisionProfileName(TEXT("BlockAllDynamic"));LeafCollision->SetGenerateOverlapEvents(false);
  EventAudio=CreateDefaultSubobject<UAudioComponent>(TEXT("DoorEventAudio"));EventAudio->SetupAttachment(Hinge);
 MotionAudio=CreateDefaultSubobject<UAudioComponent>(TEXT("DoorMotionAudio"));MotionAudio->SetupAttachment(Hinge);
 KeypadAudio=CreateDefaultSubobject<UAudioComponent>(TEXT("DoorKeypadAudio"));KeypadAudio->SetupAttachment(Hinge);
 LockAudio=CreateDefaultSubobject<UAudioComponent>(TEXT("DoorLockAudio"));LockAudio->SetupAttachment(DoorRoot);
 for(UAudioComponent* Audio:{EventAudio.Get(),MotionAudio.Get(),KeypadAudio.Get(),LockAudio.Get()})
 {
  Audio->bAutoActivate=false;Audio->bOverrideAttenuation=true;Audio->AttenuationOverrides.bAttenuate=true;Audio->AttenuationOverrides.bSpatialize=true;
  Audio->AttenuationOverrides.AttenuationShapeExtents=FVector(100,0,0);Audio->AttenuationOverrides.FalloffDistance=1100;Audio->SetRelativeLocation(FVector(85.6,5,110));
 }
 // A fast next digit must not truncate the previous recorded click or feedback tail.
 KeypadAudio->bCanPlayMultipleInstances=true;
 MotionAudio->SetVolumeMultiplier(MovementVolume);
 Prompt=CreateDefaultSubobject<UTextRenderComponent>(TEXT("Prompt"));Prompt->SetupAttachment(DoorRoot);
 Prompt->SetHorizontalAlignment(EHTA_Center);Prompt->SetVerticalAlignment(EVRTA_TextCenter);
 Prompt->SetWorldSize(3.f);Prompt->SetTextRenderColor(FColor(223,219,192));Prompt->SetVisibility(false);Prompt->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 InteractionPrompt=CreateDefaultSubobject<UWidgetComponent>(TEXT("InteractionPrompt"));
 InteractionPrompt->SetupAttachment(DoorRoot);InteractionPrompt->SetWidgetSpace(EWidgetSpace::World);
 InteractionPrompt->SetDrawSize(FVector2D(420,90));InteractionPrompt->SetPivot(FVector2D(.5,.5));
 InteractionPrompt->SetTwoSided(true);InteractionPrompt->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 InteractionPrompt->SetGenerateOverlapEvents(false);InteractionPrompt->SetCastShadow(false);InteractionPrompt->SetVisibility(false);
 static ConstructorHelpers::FObjectFinder<UMaterialInterface> PromptMaterial(TEXT("/Game/MaldekRefinement/R12/Doors/M_DoorInteractionPrompt"));
 InteractionPromptMaterial=PromptMaterial.Object;
 KeypadCamera=CreateDefaultSubobject<UCameraComponent>(TEXT("KeypadCamera"));KeypadCamera->SetupAttachment(Hinge);
 KeypadCamera->SetRelativeLocation(FVector(109.6,65,124));KeypadCamera->SetRelativeRotation((FVector(85.6,4.5,104.5)-FVector(109.6,65,124)).Rotation());KeypadCamera->SetFieldOfView(48);KeypadCamera->bConstrainAspectRatio=true;
 KeypadDisplay=CreateDefaultSubobject<UTextRenderComponent>(TEXT("KeypadDisplay"));KeypadDisplay->SetupAttachment(Hinge);
 KeypadDisplay->SetRelativeLocation(FVector(85.6,4.65,111.9));KeypadDisplay->SetRelativeRotation(FRotator(0,90,0));KeypadDisplay->SetHorizontalAlignment(EHTA_Center);KeypadDisplay->SetWorldSize(.9f);KeypadDisplay->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void AStationDoor::RefreshLockVisuals()
{
 Keypad->SetVisibility(bHasKeypad);InteriorElectronics->SetVisibility(bHasKeypad);ElectronicStrike->SetVisibility(bHasKeypad);
 KeypadDisplay->SetVisibility(bHasKeypad);KeypadDisplay->SetText(FText::FromString(bLocked?TEXT("LOCKED"):TEXT("OPEN")));KeypadDisplay->SetTextRenderColor(bLocked?FColor(160,200,170):FColor(100,230,140));
 if(StatusMaterial)StatusMaterial->SetVectorParameterValue(TEXT("StatusColor"),bLocked?FLinearColor(1,.025,.005):FLinearColor(.02,.8,.1));
}
void AStationDoor::OnConstruction(const FTransform& Transform)
{
 Super::OnConstruction(Transform);if(!bHasKeypad)bLocked=false;RefreshLockVisuals();
}
void AStationDoor::BeginPlay()
{
 Super::BeginPlay();CurrentAngle=TargetAngle=0;Hinge->SetRelativeRotation(FRotator::ZeroRotator);
 if(InteractionPromptMaterial)InteractionPrompt->SetMaterial(0,InteractionPromptMaterial);
 const TArray<FName> Slots=Keypad->GetMaterialSlotNames();
 for(int32 I=0;I<Slots.Num();++I)if(Slots[I].ToString().Contains(TEXT("D03_Status_red")))StatusMaterial=Keypad->CreateAndSetMaterialInstanceDynamic(I);
 RefreshLockVisuals();
}
bool AStationDoor::Unlock()
{
 if(!bHasKeypad || !bLocked)return false;
 GetWorldTimerManager().ClearTimer(LockSoundTimer);
 bLocked=false;PlayDoorSound(UnlockSound);EndKeypadInteraction(true);EnteredCode.Empty();RefreshLockVisuals();return true;
}
bool AStationDoor::Lock()
{
 if(!bHasKeypad || bLocked || !FMath::IsNearlyZero(CurrentAngle,.01f) || !FMath::IsNearlyZero(TargetAngle,.01f))return false;
 bLocked=true;EndKeypadInteraction(true);EnteredCode.Empty();RefreshLockVisuals();
 // Let the closing impact speak first, then hear the bolt engage in the fixed strike.
 GetWorldTimerManager().SetTimer(LockSoundTimer,[this](){if(bLocked)PlayDoorSound(LockSound);},.18f,false);
 return true;
}
bool AStationDoor::SubmitCode(const FString& Code)
{
 if(!bHasKeypad || !bLocked)return false;
 if(AccessCode.IsEmpty() || Code!=AccessCode){PlayDoorSound(RejectSound,true);bCodeRejected=true;FeedbackSeconds=2;EnteredCode.Empty();return false;}
 bCodeRejected=false;PlayDoorSound(ConfirmSound,true);return Unlock();
}
bool AStationDoor::TryInteract()
{
 if(bLocked)
 {
  APlayerController* PC=UGameplayStatics::GetPlayerController(this,0);
  if(IsInteriorSide(PC) && HasFocus(PC))Unlock();
  else {BeginKeypadInteraction(PC);return false;}
 }
 TargetAngle=FMath::IsNearlyZero(TargetAngle)?OpenAngle:0.f;bObstructed=false;return true;
}
bool AStationDoor::IsInteriorSide(APlayerController* PC) const
{
 // The keypad faces +Y. Use the closed frame and the pawn, never the swinging
 // leaf or inspection camera, so opening the door cannot swap access sides.
 return PC && PC->GetPawn() && DoorRoot->GetComponentTransform().InverseTransformPosition(PC->GetPawn()->GetActorLocation()).Y<0.f;
}
bool AStationDoor::HasFocus(APlayerController* PC) const
{
 if(!PC || !PC->GetPawn() || PC->IsMoveInputIgnored())return false;
 FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
 FCollisionQueryParams Params(SCENE_QUERY_STAT(StationDoorFocus),false,PC->GetPawn());
 FHitResult Hit;GetWorld()->LineTraceSingleByChannel(Hit,Eye,Eye+View.Vector()*InteractionDistance,ECC_Visibility,Params);
 return Hit.GetActor()==this;
}
bool AStationDoor::CanOccupyAngle(float Angle) const
{
 const FTransform Candidate(FRotator(0,Angle,0),FVector::ZeroVector,FVector::OneVector);
 const FTransform World=Candidate*DoorRoot->GetComponentTransform();
 FCollisionQueryParams Params(SCENE_QUERY_STAT(StationDoorObstruction),false,this);
 // Same full leaf volume as walking collision. Exclude self, include player and walls.
 const FVector Center=World.TransformPosition(LeafCollision->GetRelativeLocation());
 const FVector Extent=LeafCollision->GetUnscaledBoxExtent()*World.GetScale3D().GetAbs();
 return !GetWorld()->OverlapBlockingTestByChannel(Center,World.GetRotation(),ECC_Pawn,FCollisionShape::MakeBox(Extent),Params);
}
void AStationDoor::Tick(float Dt)
{
 Super::Tick(Dt);ShowDoorHint(false);Prompt->SetVisibility(false);APlayerController* PC=UGameplayStatics::GetPlayerController(this,0);
 FeedbackSeconds=FMath::Max(0.f,FeedbackSeconds-Dt);
 if(bEnteringCode)
 {
  if(!KeypadController.IsValid() || !PC || !PC->GetPawn() || PC!=KeypadController.Get() || (KeypadBlendRemaining<=0 && PC->GetViewTarget()!=this))
   EndKeypadInteraction(false);
  else
  {
   KeypadBlendRemaining=FMath::Max(0.f,KeypadBlendRemaining-Dt);
   const int32 Hover=HoveredKeypadButton(PC);PC->CurrentMouseCursor=Hover>=0?EMouseCursor::Hand:EMouseCursor::Default;
   if(PC->WasInputKeyJustPressed(EKeys::Escape) || PC->WasInputKeyJustPressed(EKeys::RightMouseButton) || PC->WasInputKeyJustPressed(EKeys::E))CancelKeypadInteraction();
   else if(KeypadBlendRemaining<=0)
   {
    if(PC->WasInputKeyJustPressed(EKeys::LeftMouseButton) && Hover>=0)PressKeypadButton(Hover);
    const FKey Digits[]={EKeys::Zero,EKeys::One,EKeys::Two,EKeys::Three,EKeys::Four,EKeys::Five,EKeys::Six,EKeys::Seven,EKeys::Eight,EKeys::Nine};
    const FKey NumPad[]={EKeys::NumPadZero,EKeys::NumPadOne,EKeys::NumPadTwo,EKeys::NumPadThree,EKeys::NumPadFour,EKeys::NumPadFive,EKeys::NumPadSix,EKeys::NumPadSeven,EKeys::NumPadEight,EKeys::NumPadNine};
    for(int32 I=0;I<10 && bEnteringCode;++I)if(PC->WasInputKeyJustPressed(Digits[I]) || PC->WasInputKeyJustPressed(NumPad[I]))PressKeypadButton(I==0?10:I-1);
    if(bEnteringCode && PC->WasInputKeyJustPressed(EKeys::BackSpace)){EnteredCode=EnteredCode.LeftChop(1);bCodeRejected=false;PlayDoorSound(ClearSound,true);}
    if(bEnteringCode && PC->WasInputKeyJustPressed(EKeys::Enter))PressKeypadButton(11);
   }
   if(bEnteringCode)
   {
    KeypadDisplay->SetText(FText::FromString(bCodeRejected && FeedbackSeconds>0?TEXT("TRY AGAIN"):EnteredCode.IsEmpty()?TEXT("ENTER CODE"):FString::ChrN(EnteredCode.Len(),TEXT('*'))));
    ShowDoorHint(true,TEXT("Return to door"),TEXT("Click keypad buttons   /   OK to confirm"));
   }
  }
 }
 else
 {
  const bool Focus=HasFocus(PC);
  if(Focus)
  {
   const bool bNeedsCode=bLocked && !IsInteriorSide(PC);
   ShowDoorHint(true,bNeedsCode?TEXT("Use keypad"):bObstructed?TEXT("Retry door"):FMath::IsNearlyZero(TargetAngle)?TEXT("Open door"):TEXT("Close door"),bNeedsCode?TEXT("SECURED ACCESS"):bObstructed?TEXT("Clear the doorway to continue"):TEXT("STATION ACCESS"));
   if(PC->WasInputKeyJustPressed(EKeys::E))TryInteract();
  }
 }
 const float PreviousAngle=CurrentAngle;
 if(!bLocked && !FMath::IsNearlyEqual(CurrentAngle,TargetAngle,.01f))
 {
  const float Next=FMath::FInterpConstantTo(CurrentAngle,TargetAngle,Dt,DegreesPerSecond);
  // Subdivide rotation to prevent tunnelling on a slow frame.
  const int32 Steps=FMath::Max(1,FMath::CeilToInt(FMath::Abs(Next-CurrentAngle)/.5f));
  const float Start=CurrentAngle;
  for(int32 I=1;I<=Steps;++I)
  {
   const float A=FMath::Lerp(Start,Next,float(I)/Steps);
   if(!CanOccupyAngle(A)){TargetAngle=CurrentAngle;bObstructed=true;break;}
   CurrentAngle=A;Hinge->SetRelativeRotation(FRotator(0,CurrentAngle,0));
  }
 }
 const bool bMoving=!FMath::IsNearlyEqual(PreviousAngle,CurrentAngle,.001f);
 const bool bClosing=FMath::Abs(CurrentAngle)<FMath::Abs(PreviousAngle);
 USoundBase* TravelSound=bClosing && ClosingMovementSound?ClosingMovementSound.Get():MovementSound.Get();
 if(bMoving && FMath::IsNearlyZero(PreviousAngle,.01f))PlayDoorSound(UnlatchSound);
 if(bMoving && TravelSound && (!MotionAudio->IsPlaying() || MotionAudio->Sound!=TravelSound)){MotionAudio->Stop();MotionAudio->SetSound(TravelSound);MotionAudio->FadeIn(.035f,MovementVolume);}
 else if(!bMoving && MotionAudio->IsPlaying())MotionAudio->Stop();
 if(FMath::Abs(PreviousAngle)>.01f && FMath::IsNearlyZero(CurrentAngle,.01f) && FMath::IsNearlyZero(TargetAngle))
 {
  MotionAudio->Stop();PlayDoorSound(CloseSound);if(bRelockOnClose)Lock();
 }
}
FVector AStationDoor::GetKeypadButtonWorldPosition(int32 Index) const
{
 if(Index<0 || Index>=12)return FVector::ZeroVector;
 return Hinge->GetComponentTransform().TransformPosition(FVector(85.6+(Index%3-1)*3.3,4.96,107.7-(Index/3)*3.1));
}
int32 AStationDoor::HoveredKeypadButton(APlayerController* PC) const
{
 FVector Origin,Direction;if(!PC || !PC->DeprojectMousePositionToWorld(Origin,Direction))return INDEX_NONE;
 const FTransform T=Hinge->GetComponentTransform();Origin=T.InverseTransformPosition(Origin);Direction=T.InverseTransformVector(Direction);
 if(Direction.Y>=-KINDA_SMALL_NUMBER)return INDEX_NONE;
 const double Distance=(4.96-Origin.Y)/Direction.Y;if(Distance<0)return INDEX_NONE;
 const FVector Hit=Origin+Direction*Distance;
 for(int32 I=0;I<12;++I)
  if(FMath::Abs(Hit.X-(85.6+(I%3-1)*3.3))<=1.25 && FMath::Abs(Hit.Z-(107.7-(I/3)*3.1))<=1.05)return I;
 return INDEX_NONE;
}
bool AStationDoor::BeginKeypadInteraction(APlayerController* PC)
{
 if(bEnteringCode || !bHasKeypad || !bLocked || !PC || !PC->IsLocalController() || !HasFocus(PC))return false;
 KeypadController=PC;PreviousViewTarget=PC->GetViewTarget();PreviousPawn=PC->GetPawn();bPreviousMouseCursor=PC->bShowMouseCursor;
 PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);
 if(ACharacter* Character=Cast<ACharacter>(PreviousPawn.Get()))
 {
  auto* Movement=Character->GetCharacterMovement();PreviousMovementMode=uint8(Movement->MovementMode);PreviousCustomMovementMode=Movement->CustomMovementMode;
  Movement->StopMovementImmediately();Movement->DisableMovement();Character->StopJumping();
 }
 TInlineComponentArray<UMeshComponent*> Meshes(PreviousPawn.Get());
 for(UMeshComponent* Mesh:Meshes)if(!Mesh->bHiddenInGame){HiddenPlayerMeshes.Add(Mesh);Mesh->SetHiddenInGame(true);}
 EnteredCode.Empty();bCodeRejected=false;bEnteringCode=true;KeypadBlendRemaining=.5f;
 FInputModeGameAndUI Mode;Mode.SetHideCursorDuringCapture(false);Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);PC->SetInputMode(Mode);PC->bShowMouseCursor=true;
 int32 Width,Height;PC->GetViewportSize(Width,Height);PC->SetMouseLocation(Width/2,Height/2);
 PC->SetViewTargetWithBlend(this,.35f,VTBlend_Cubic,0,true);Prompt->SetVisibility(false);return true;
}
void AStationDoor::PressKeypadButton(int32 Index)
{
 if(!bEnteringCode || Index<0 || Index>=12)return;
 if(Index==11){PlayDoorSound(ButtonSound,true);SubmitCode(EnteredCode);return;}
 bCodeRejected=false;
 if(Index==9){PlayDoorSound(ClearSound,true);EnteredCode.Empty();}
 else if(EnteredCode.Len()<8){PlayDoorSound(ButtonSound,true);EnteredCode+=FString::FromInt(Index==10?0:Index+1);}
 else {PlayDoorSound(RejectSound,true);bCodeRejected=true;FeedbackSeconds=.6f;}
}
void AStationDoor::CancelKeypadInteraction()
{
 EndKeypadInteraction(true);RefreshLockVisuals();
}
void AStationDoor::EndKeypadInteraction(bool bBlend)
{
 if(!bEnteringCode)return;
 bEnteringCode=false;EnteredCode.Empty();Prompt->SetVisibility(false);
 if(APlayerController* PC=KeypadController.Get())
 {
  if(PC->GetViewTarget()==this || KeypadBlendRemaining>0)
   if(AActor* Target=PreviousViewTarget.IsValid()?PreviousViewTarget.Get():PC->GetPawn())PC->SetViewTargetWithBlend(Target,bBlend?.3f:0.f,VTBlend_Cubic,0,true);
  PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);PC->bShowMouseCursor=bPreviousMouseCursor;PC->CurrentMouseCursor=EMouseCursor::Default;
  PC->SetInputMode(FInputModeGameOnly());
 }
 if(ACharacter* Character=Cast<ACharacter>(PreviousPawn.Get()))
 {
  Character->StopJumping();Character->GetCharacterMovement()->SetMovementMode(EMovementMode(PreviousMovementMode),PreviousCustomMovementMode);
 }
 for(auto& Mesh:HiddenPlayerMeshes)if(Mesh.IsValid())Mesh->SetHiddenInGame(false);
 HiddenPlayerMeshes.Empty();KeypadController.Reset();PreviousViewTarget.Reset();PreviousPawn.Reset();KeypadBlendRemaining=0;
}
void AStationDoor::EndPlay(const EEndPlayReason::Type Reason)
{
 GetWorldTimerManager().ClearTimer(LockSoundTimer);
 EndKeypadInteraction(false);InteractionPrompt->SetSlateWidget(nullptr);HintWidget.Reset();MotionAudio->Stop();EventAudio->Stop();KeypadAudio->Stop();LockAudio->Stop();Super::EndPlay(Reason);
}


void AStationDoor::PlayDoorSound(USoundBase* Sound,bool bKeypad)
{
 if(!Sound)return;
 UAudioComponent* Audio=bKeypad?KeypadAudio.Get():(Sound==UnlockSound || Sound==LockSound?LockAudio.Get():EventAudio.Get());
 Audio->SetRelativeLocation(bKeypad?FVector(85.6,5,105):FVector(111,0,112));Audio->SetSound(Sound);
 Audio->SetVolumeMultiplier(bKeypad?KeypadVolume:DoorVolume);Audio->SetPitchMultiplier(1.f);Audio->Play();
}
void AStationDoor::ShowDoorHint(bool bVisible,const FString& Action,const FString& Detail)
{
 if(!HintWidget.IsValid() && bVisible)
 {
  using namespace StationInteractionStyle;
  HintWidget=SNew(SOverlay)
   +SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
   [SNew(SBorder).BorderImage(&OuterRule).Padding(1)
    [SNew(SBorder).BorderImage(&RuleGap).Padding(3)
     [SNew(SBorder).BorderImage(&InnerRule).Padding(1)
      [SNew(SBorder).BorderImage(&Panel).Padding(FMargin(15,10))
    [SNew(SHorizontalBox)
     +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,15,0)
     [SNew(SBox).WidthOverride(40).HeightOverride(40)
      [SNew(SBorder).BorderImage(&Key).HAlign(HAlign_Center).VAlign(VAlign_Center)
       [SNew(STextBlock).Text(FText::FromString(TEXT("E"))).Font(FCoreStyle::GetDefaultFontStyle("Bold",20)).ColorAndOpacity(Ink)]]]
     +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
     [SNew(SVerticalBox)
      +SVerticalBox::Slot().AutoHeight()[SAssignNew(HintAction,STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",17)).ColorAndOpacity(StationInteractionStyle::Action)]
      +SVerticalBox::Slot().AutoHeight().Padding(0,4,0,0)[SAssignNew(HintDetail,STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",10)).ColorAndOpacity(StationInteractionStyle::Detail)]]]]]]];
  InteractionPrompt->SetSlateWidget(HintWidget);
 }
 InteractionPrompt->SetVisibility(bVisible);
 if(bVisible)
 {
  if(APlayerController* PC=UGameplayStatics::GetPlayerController(this,0))
  {
   FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
   const FTransform LeafTransform=Hinge->GetComponentTransform();
   const float Side=LeafTransform.InverseTransformPosition(Eye).Y<0.f?-1.f:1.f;
   InteractionPrompt->SetWorldLocation(LeafTransform.TransformPosition(bEnteringCode?FVector(85.6,14,95):FVector(50,Side*20,116)));
   InteractionPrompt->SetWorldRotation((Eye-InteractionPrompt->GetComponentLocation()).Rotation());
   InteractionPrompt->SetWorldScale3D(FVector(bEnteringCode?.035f:.16f));
  }
 }
 if(HintWidget.IsValid())
 {
  HintWidget->SetVisibility(bVisible?EVisibility::HitTestInvisible:EVisibility::Collapsed);
  if(bVisible){HintAction->SetText(FText::FromString(Action));HintDetail->SetText(FText::FromString(Detail));}
 }
}
