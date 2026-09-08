#include "StationDoor.h"
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
 bLocked=false;bEnteringCode=false;EnteredCode.Empty();RefreshLockVisuals();return true;
}
bool AStationDoor::SubmitCode(const FString& Code)
{
 if(!bHasKeypad || !bLocked)return false;
 if(AccessCode.IsEmpty() || Code!=AccessCode){bCodeRejected=true;FeedbackSeconds=2;EnteredCode.Empty();return false;}
 bCodeRejected=false;return Unlock();
}
bool AStationDoor::TryInteract()
{
 if(bLocked){bEnteringCode=true;EnteredCode.Empty();return false;}
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
 const bool Focus=HasFocus(PC);FeedbackSeconds=FMath::Max(0.f,FeedbackSeconds-Dt);
 if(!Focus){bEnteringCode=false;EnteredCode.Empty();}
 Prompt->SetVisibility(Focus);
 if(Focus)
 {
  FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
  const FVector Handle=Hinge->GetComponentTransform().TransformPosition(FVector(111,0,112));
  Prompt->SetWorldLocation(Handle+(Eye-Handle).GetSafeNormal()*12+FVector(0,0,13));
  Prompt->SetWorldRotation((Eye-Prompt->GetComponentLocation()).Rotation());
  if(bEnteringCode)
  {
   const FKey Digits[]={EKeys::Zero,EKeys::One,EKeys::Two,EKeys::Three,EKeys::Four,EKeys::Five,EKeys::Six,EKeys::Seven,EKeys::Eight,EKeys::Nine};
   const FKey NumPad[]={EKeys::NumPadZero,EKeys::NumPadOne,EKeys::NumPadTwo,EKeys::NumPadThree,EKeys::NumPadFour,EKeys::NumPadFive,EKeys::NumPadSix,EKeys::NumPadSeven,EKeys::NumPadEight,EKeys::NumPadNine};
   for(int32 I=0;I<10;++I)if(EnteredCode.Len()<8 && (PC->WasInputKeyJustPressed(Digits[I]) || PC->WasInputKeyJustPressed(NumPad[I])))EnteredCode+=FString::FromInt(I);
   if(PC->WasInputKeyJustPressed(EKeys::BackSpace))EnteredCode=EnteredCode.LeftChop(1);
   if(PC->WasInputKeyJustPressed(EKeys::Escape)){bEnteringCode=false;EnteredCode.Empty();}
   if(PC->WasInputKeyJustPressed(EKeys::Enter) || PC->WasInputKeyJustPressed(EKeys::E))SubmitCode(EnteredCode);
  }
  else if(PC->WasInputKeyJustPressed(EKeys::E))TryInteract();
  const FString Hint=bEnteringCode?FString::Printf(TEXT("CODE  %s\n0-9   E/Enter confirm   Backspace clear"),*FString::ChrN(EnteredCode.Len(),TEXT('*'))):bLocked?TEXT("E  Use keypad"):bObstructed?TEXT("Door blocked - E to retry"):FMath::IsNearlyZero(TargetAngle)?TEXT("E  Open"):TEXT("E  Close");
  Prompt->SetText(FText::FromString(bCodeRejected && FeedbackSeconds>0?TEXT("Code not accepted"):Hint));
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
