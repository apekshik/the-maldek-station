#include "StationCabinet.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Components/WidgetComponent.h"
#include "Components/AudioComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "InputCoreTypes.h"
#include "Sound/SoundBase.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"
#include "StationInteractionStyle.h"

AStationCabinet::AStationCabinet()
{
 PrimaryActorTick.bCanEverTick=true;
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
 Pivot=CreateDefaultSubobject<USceneComponent>(TEXT("Pivot"));Pivot->SetupAttachment(RootComponent);
 MovingMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MovingMesh"));MovingMesh->SetupAttachment(Pivot);
 MovingMesh->SetMobility(EComponentMobility::Movable);MovingMesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
 MovingMesh->SetCollisionResponseToAllChannels(ECR_Ignore);MovingMesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
 InteractionPrompt=CreateDefaultSubobject<UWidgetComponent>(TEXT("InteractionPrompt"));InteractionPrompt->SetupAttachment(RootComponent);
 InteractionPrompt->SetWidgetSpace(EWidgetSpace::World);InteractionPrompt->SetDrawSize(FVector2D(420,90));InteractionPrompt->SetTwoSided(true);
 InteractionPrompt->SetCollisionEnabled(ECollisionEnabled::NoCollision);InteractionPrompt->SetCastShadow(false);InteractionPrompt->SetVisibility(false);
 static ConstructorHelpers::FObjectFinder<UMaterialInterface> Mat(TEXT("/Game/MaldekRefinement/R12/Doors/M_DoorInteractionPrompt"));
 if(Mat.Succeeded())InteractionPrompt->SetMaterial(0,Mat.Object);
 MotionAudio=CreateDefaultSubobject<UAudioComponent>(TEXT("MotionAudio"));MotionAudio->SetupAttachment(Pivot);MotionAudio->bAutoActivate=false;
 MotionAudio->bOverrideAttenuation=true;MotionAudio->AttenuationOverrides.bAttenuate=true;MotionAudio->AttenuationOverrides.bSpatialize=true;
 MotionAudio->AttenuationOverrides.AttenuationShapeExtents=FVector(40,0,0);MotionAudio->AttenuationOverrides.FalloffDistance=600;MotionAudio->SetVolumeMultiplier(.45f);
}
void AStationCabinet::OnConstruction(const FTransform& Transform)
{
 Super::OnConstruction(Transform);
 RebuildCollision();
 Progress=Target=0;bWantsOpen=bObstructed=false;Pivot->SetRelativeTransform(Pose(0));MotionAudio->SetRelativeLocation(FocusLocation);
}
void AStationCabinet::RebuildCollision()
{
 TArray<UBoxComponent*> Previous;GetComponents(Previous);
 for(auto B:Previous)if(B->ComponentHasTag(TEXT("KitchenMovingCollision"))){RemoveInstanceComponent(B);B->DestroyComponent();}
 Boxes.Reset();
 for(int32 I=0;I<FMath::Min(CollisionCenters.Num(),CollisionExtents.Num());++I)
 {
  auto B=NewObject<UBoxComponent>(this);B->ComponentTags.Add(TEXT("KitchenMovingCollision"));AddInstanceComponent(B);
  B->SetupAttachment(Pivot);B->SetMobility(EComponentMobility::Movable);B->SetRelativeLocation(CollisionCenters[I]);B->SetBoxExtent(CollisionExtents[I]);
  B->SetCollisionProfileName(TEXT("BlockAllDynamic"));B->SetCollisionResponseToChannel(ECC_Visibility,ECR_Ignore);B->SetGenerateOverlapEvents(false);B->RegisterComponent();Boxes.Add(B);
 }
}
FTransform AStationCabinet::Pose(float Fraction) const
{
 return FTransform(FRotator(0,bSliding?0:OpenAngle*Fraction,0),bSliding?OpenOffset*Fraction:FVector::ZeroVector);
}
bool AStationCabinet::CanOccupy(float Fraction) const
{
 const FTransform W=Pose(Fraction)*GetActorTransform();FCollisionQueryParams Q(SCENE_QUERY_STAT(CabinetObstruction),true,this);
 for(int32 I=0;I<FMath::Min(CollisionCenters.Num(),CollisionExtents.Num());++I)
 {
  const FVector E=(CollisionExtents[I]-FVector(.05f)).ComponentMax(FVector(.05f));
  TArray<FOverlapResult> Hits;
  if(GetWorld()->OverlapMultiByChannel(Hits,W.TransformPosition(CollisionCenters[I]),W.GetRotation(),ECC_Pawn,FCollisionShape::MakeBox(E),Q))
  {
   for(const auto& Hit:Hits)if(Hit.bBlockingHit)UE_LOG(LogTemp,Display,TEXT("Cabinet obstruction %s piece %d fraction %.3f by %s / %s"),*GetName(),I,Fraction,*GetNameSafe(Hit.GetActor()),*GetNameSafe(Hit.GetComponent()));
   return false;
  }
 }
 return true;
}
bool AStationCabinet::HasFocus(APlayerController* PC) const
{
 if(!PC || !PC->GetPawn() || PC->IsMoveInputIgnored())return false;
 FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(CabinetFocus),true,PC->GetPawn());
 GetWorld()->LineTraceSingleByChannel(Hit,Eye,Eye+View.Vector()*200,ECC_Visibility,Q);return Hit.GetActor()==this;
}
bool AStationCabinet::TryInteract()
{
 if(!bObstructed)bWantsOpen=!bWantsOpen;
 Target=bWantsOpen?1:0;bObstructed=false;
 if(USoundBase* Sound=bWantsOpen?MovementSound.Get():ClosingSound.Get()){MotionAudio->SetSound(Sound);MotionAudio->Play();}
 return true;
}
void AStationCabinet::Tick(float Dt)
{
 Super::Tick(Dt);auto PC=UGameplayStatics::GetPlayerController(this,0);const bool Focus=HasFocus(PC);ShowHint(Focus);
 if(Focus && PC->WasInputKeyJustPressed(EKeys::E))TryInteract();
 const float Next=FMath::FInterpConstantTo(Progress,Target,Dt,1/FMath::Max(.1f,SecondsToOpen));
 const float Travel=bSliding?OpenOffset.Size():FMath::Abs(OpenAngle);
 const int32 Steps=FMath::Max(1,FMath::CeilToInt(FMath::Abs(Next-Progress)*Travel/(bSliding?.5f:2.f)));
 const float Start=Progress;
 for(int32 I=1;I<=Steps && !FMath::IsNearlyEqual(Progress,Target);++I)
 {
  const float P=FMath::Lerp(Start,Next,float(I)/Steps);
  if(!CanOccupy(P)){Target=Progress;bObstructed=true;MotionAudio->Stop();break;}
  Progress=P;Pivot->SetRelativeTransform(Pose(P));
 }
 if(FMath::IsNearlyEqual(Progress,Target))MotionAudio->Stop();
}

void AStationCabinet::ShowHint(bool bVisible)
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
   const FVector Point=Pivot->GetComponentTransform().TransformPosition(FocusLocation);
   InteractionPrompt->SetWorldLocation(Point+(Eye-Point).GetSafeNormal()*12+FVector(0,0,15));
   InteractionPrompt->SetWorldRotation((Eye-InteractionPrompt->GetComponentLocation()).Rotation());
   InteractionPrompt->SetWorldScale3D(FVector(.075f));
  }
 }
 if(HintWidget.IsValid())
 {
  HintWidget->SetVisibility(bVisible?EVisibility::HitTestInvisible:EVisibility::Collapsed);
  if(bVisible){HintAction->SetText(FText::FromString((bObstructed?TEXT("Retry "):bWantsOpen?TEXT("Close "):TEXT("Open "))+DisplayName));HintDetail->SetText(FText::FromString(bObstructed?TEXT("Clear the moving front"):TEXT("STATION STORAGE")));}
 }
}
