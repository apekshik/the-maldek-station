#include "StationDoor.h"
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
 Prompt=CreateDefaultSubobject<UTextRenderComponent>(TEXT("Prompt"));Prompt->SetupAttachment(DoorRoot);
 Prompt->SetHorizontalAlignment(EHTA_Center);Prompt->SetVerticalAlignment(EVRTA_TextCenter);
 Prompt->SetWorldSize(3.f);Prompt->SetTextRenderColor(FColor(223,219,192));Prompt->SetVisibility(false);Prompt->SetCollisionEnabled(ECollisionEnabled::NoCollision);
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
 const TArray<FName> Slots=Keypad->GetMaterialSlotNames();
 for(int32 I=0;I<Slots.Num();++I)if(Slots[I].ToString().Contains(TEXT("D03_Status_red")))StatusMaterial=Keypad->CreateAndSetMaterialInstanceDynamic(I);
 RefreshLockVisuals();
}
bool AStationDoor::Unlock()
{
 if(!bHasKeypad || !bLocked)return false;
 bLocked=false;EndKeypadInteraction(true);EnteredCode.Empty();RefreshLockVisuals();return true;
}
bool AStationDoor::SubmitCode(const FString& Code)
{
 if(!bHasKeypad || !bLocked)return false;
 if(AccessCode.IsEmpty() || Code!=AccessCode){bCodeRejected=true;FeedbackSeconds=2;EnteredCode.Empty();return false;}
 bCodeRejected=false;return Unlock();
}
bool AStationDoor::TryInteract()
{
 if(bLocked){BeginKeypadInteraction(UGameplayStatics::GetPlayerController(this,0));return false;}
 TargetAngle=FMath::IsNearlyZero(TargetAngle)?OpenAngle:0.f;bObstructed=false;return true;
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
 Super::Tick(Dt);APlayerController* PC=UGameplayStatics::GetPlayerController(this,0);
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
    if(bEnteringCode && PC->WasInputKeyJustPressed(EKeys::BackSpace)){EnteredCode=EnteredCode.LeftChop(1);bCodeRejected=false;}
    if(bEnteringCode && PC->WasInputKeyJustPressed(EKeys::Enter))PressKeypadButton(11);
   }
   if(bEnteringCode)
   {
    KeypadDisplay->SetText(FText::FromString(bCodeRejected && FeedbackSeconds>0?TEXT("TRY AGAIN"):EnteredCode.IsEmpty()?TEXT("ENTER CODE"):FString::ChrN(EnteredCode.Len(),TEXT('*'))));
    const FVector Hint=Hinge->GetComponentTransform().TransformPosition(FVector(85.6,5,90));
    Prompt->SetWorldLocation(Hint);Prompt->SetWorldRotation((KeypadCamera->GetComponentLocation()-Hint).Rotation());Prompt->SetWorldSize(.8f);
    Prompt->SetText(FText::FromString(TEXT("Click buttons  |  OK confirm\nE / right-click to leave")));Prompt->SetVisibility(true);
   }
  }
 }
 else
 {
  const bool Focus=HasFocus(PC);Prompt->SetVisibility(Focus);Prompt->SetWorldSize(3);
  if(Focus)
  {
   FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
   const FVector Handle=Hinge->GetComponentTransform().TransformPosition(FVector(111,0,112));
   Prompt->SetWorldLocation(Handle+(Eye-Handle).GetSafeNormal()*12+FVector(0,0,13));Prompt->SetWorldRotation((Eye-Prompt->GetComponentLocation()).Rotation());
   Prompt->SetText(FText::FromString(bLocked?TEXT("E  Use keypad"):bObstructed?TEXT("Door blocked - E to retry"):FMath::IsNearlyZero(TargetAngle)?TEXT("E  Open"):TEXT("E  Close")));
   if(PC->WasInputKeyJustPressed(EKeys::E))TryInteract();
  }
 }
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
 if(Index==11){SubmitCode(EnteredCode);return;}
 bCodeRejected=false;
 if(Index==9)EnteredCode.Empty();
 else if(EnteredCode.Len()<8)EnteredCode+=FString::FromInt(Index==10?0:Index+1);
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
 EndKeypadInteraction(false);Super::EndPlay(Reason);
}
