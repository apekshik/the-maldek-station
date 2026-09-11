#include "StationInspectionComponent.h"
#include "StationInspectable.h"
#include "StationInteractionStyle.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/SLeafWidget.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SCanvas.h"
#include "Widgets/Images/SImage.h"
#include "Brushes/SlateRoundedBoxBrush.h"
#include "Blueprint/WidgetLayoutLibrary.h"
#include "Widgets/Layout/SWrapBox.h"
#include "Rendering/DrawElements.h"

namespace
{
const FSlateRoundedBoxBrush AimDotBrush(FLinearColor::White,FLinearColor::Black,1.f);
const FLinearColor InspectionWhite(.95f,.95f,.92f,1.f);
const FLinearColor InspectionShadow(0.f,0.f,0.f,.85f);
// Slate geometry keeps the mouse hints crisp at any viewport DPI.
class SInspectionMouseIcon final : public SLeafWidget
{
public:
 SLATE_BEGIN_ARGS(SInspectionMouseIcon) : _Wheel(false) {} SLATE_ARGUMENT(bool,Wheel) SLATE_END_ARGS()
 void Construct(const FArguments& Args){bWheel=Args._Wheel;}
 virtual FVector2D ComputeDesiredSize(float) const override{return FVector2D(27,30);}
 virtual int32 OnPaint(const FPaintArgs&,const FGeometry& G,const FSlateRect&,FSlateWindowElementList& Out,int32 Layer,const FWidgetStyle&,bool) const override
 {
  auto Line=[&](std::initializer_list<FVector2D> Points,float Width=1.5f)
  {
   TArray<FVector2D> P;for(const FVector2D& V:Points)P.Add(V);
   FSlateDrawElement::MakeLines(Out,Layer,G.ToPaintGeometry(),P,ESlateDrawEffect::None,StationInteractionStyle::Action,true,Width);
  };
  Line({{8,3},{6,5},{5,9},{5,21},{7,25},{11,27},{15,27},{19,25},{21,21},{21,9},{20,5},{18,3},{8,3}});
  Line({{13,3},{13,13}});Line({{5,13},{21,13}});
  if(bWheel)
  {
   Line({{13,6},{13,10}},3);Line({{25,5},{25,24}});
   Line({{22,8},{25,5},{27,8}});Line({{22,21},{25,24},{27,21}});
  }
  else {Line({{9,6},{9,10}},4);}
  return Layer;
 }
private: bool bWheel=false;
};
TSharedRef<SWidget> InspectionKey(const TCHAR* Label)
{
 return SNew(STextBlock).Text(FText::FromString(FString::Printf(TEXT("[ %s ]"),Label)))
  .Font(FCoreStyle::GetDefaultFontStyle("Bold",11)).ColorAndOpacity(StationInteractionStyle::Action)
  .ShadowOffset(FVector2D(1,1)).ShadowColorAndOpacity(InspectionShadow);
}
TSharedRef<SWidget> InspectionHint(TSharedRef<SWidget> Icon,const TCHAR* Label)
{
 return SNew(SHorizontalBox)
  +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[Icon]
  +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(7,0,0,0)
   [SNew(STextBlock).Text(FText::FromString(Label)).Font(FCoreStyle::GetDefaultFontStyle("Regular",12)).ColorAndOpacity(InspectionWhite).ShadowOffset(FVector2D(1,1)).ShadowColorAndOpacity(InspectionShadow)];
}
}

UStationInspectionComponent::UStationInspectionComponent()
{
 PrimaryComponentTick.bCanEverTick=true;
 PrimaryComponentTick.TickGroup=TG_PostUpdateWork;
}

APlayerController* UStationInspectionComponent::Player() const {return Cast<APlayerController>(GetOwner());}

bool UStationInspectionComponent::CanSearch() const
{
 const APlayerController* PC=Player();
 return PC && PC->IsLocalController() && PC->GetPawn() && !PC->IsPaused()
  && !PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored() && !PC->bShowMouseCursor
  && PC->GetViewTarget()==PC->GetPawn() && !IsInspectingObject() && GFrameCounter>InputSuppressedFrame;
}

AStationInspectable* UStationInspectionComponent::FindFocusedObject() const
{
 if(!CanSearch())return nullptr;
 APlayerController* PC=Player();
 FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
 FCollisionQueryParams Query(SCENE_QUERY_STAT(StationInspectionFocus),true,PC->GetPawn());
 FHitResult Hit;
 GetWorld()->LineTraceSingleByChannel(Hit,Eye,Eye+View.Vector()*FMath::Clamp(Reach,50.f,400.f),ECC_Visibility,Query);
 AStationInspectable* Object=Cast<AStationInspectable>(Hit.GetActor());
 if(Object && Object->bCanInspect && !Object->IsHidden())return Object;
 // A small aim allowance makes handheld props selectable without pixel hunting.
 // Each candidate still needs a clear visibility ray; walls and doors block pickup.
 TArray<FHitResult> Nearby;
 FCollisionObjectQueryParams Types;Types.AddObjectTypesToQuery(ECC_WorldDynamic);
 GetWorld()->SweepMultiByObjectType(Nearby,Eye,Eye+View.Vector()*FMath::Clamp(Reach,50.f,400.f),FQuat::Identity,Types,FCollisionShape::MakeSphere(4.f),Query);
 for(const FHitResult& Candidate:Nearby)
 {
  Object=Cast<AStationInspectable>(Candidate.GetActor());
  if(!Object || !Object->bCanInspect || Object->IsHidden())continue;
  const FVector Target=Object->Mesh->Bounds.Origin;
  if(FVector::Distance(Eye,Target)>Reach)continue;
  FCollisionQueryParams Visibility(Query);Visibility.bTraceComplex=false;
  FHitResult Occluder;GetWorld()->LineTraceSingleByChannel(Occluder,Eye,Target,ECC_Visibility,Visibility);
  if(Occluder.GetActor()==Object)return Object;
 }
 return nullptr;
}

bool UStationInspectionComponent::BeginInspection(AStationInspectable* Object)
{
 if(!IsValid(Object) || Object!=FindFocusedObject() || !Object->Mesh || !Object->Mesh->GetStaticMesh())return false;
 // An independently simulated child cannot be carried as a coherent prop.
 TInlineComponentArray<UPrimitiveComponent*> Components(Object);
 for(UPrimitiveComponent* Body:Components)
  if(Body->Mobility!=EComponentMobility::Movable || (Body!=Object->GetRootComponent() && Body->IsSimulatingPhysics()))return false;
 const FBox Bounds=Object->CalculateComponentsBoundingBoxInLocalSpace();
 const float Radius=Bounds.GetExtent().Size()*Object->GetActorScale3D().GetAbsMax();
 if(!Bounds.IsValid || Radius<.1f || Radius>65.f)return false;

 APlayerController* PC=Player();
 FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
 FActorSpawnParameters Spawn;Spawn.ObjectFlags|=RF_Transient;
 InspectionCamera=GetWorld()->SpawnActor<ACameraActor>(Eye,View,Spawn);
 if(!InspectionCamera)return false;
 InspectionCamera->GetCameraComponent()->SetFieldOfView(FMath::Clamp(InspectionFOV,35.f,80.f));
 InspectionCamera->GetCameraComponent()->bConstrainAspectRatio=false;
 InspectionCamera->GetCameraComponent()->PostProcessSettings.bOverride_VignetteIntensity=true;
 InspectionCamera->GetCameraComponent()->PostProcessSettings.VignetteIntensity=.5f;
 // Keep near clipping safe at maximum zoom; fit both horizontal and vertical FOV.
 int32 Width=0,Height=0;PC->GetViewportSize(Width,Height);
 const float Aspect=Height>0?float(Width)/Height:16.f/9.f;
 const float HalfFov=FMath::Atan(FMath::Tan(FMath::DegreesToRadians(InspectionCamera->GetCameraComponent()->FieldOfView*.5f))/FMath::Max(Aspect,1.f));
 MinimumDistance=FMath::Max(Radius+GNearClippingPlane+5.f,Radius/FMath::Sin(HalfFov)*1.05f);
 HomeDistance=MinimumDistance*1.35f;MaximumDistance=HomeDistance*1.8f;
 TargetDistance=Distance=HomeDistance;
 // A soft camera-side fill keeps fine markings readable in the station's dark rooms.
 UPointLightComponent* Fill=NewObject<UPointLightComponent>(InspectionCamera,TEXT("InspectionFill"));
 Fill->SetupAttachment(InspectionCamera->GetRootComponent());
 Fill->SetRelativeLocation(FVector(12,-24,24));Fill->SetIntensityUnits(ELightUnits::Lumens);
 Fill->SetIntensity(.15f);Fill->SetLightColor(FLinearColor(1.f,.88f,.71f));
 Fill->SetAttenuationRadius(MaximumDistance+Radius+80);Fill->SetSourceRadius(12);
 Fill->SetCastShadows(false);Fill->RegisterComponent();
 OriginalWorld=Object->GetActorTransform();OriginalRelative=Object->GetRootComponent()->GetRelativeTransform();
 SavedParent=Object->GetRootComponent()->GetAttachParent();SavedSocket=Object->GetRootComponent()->GetAttachSocketName();
 LocalCenter=Bounds.GetCenter();
 HomeRotation=(View.Quaternion()*Object->InspectionRotation.Quaternion()).GetNormalized();
 TargetRotation=CurrentRotation=HomeRotation;
 SavedPawn=PC->GetPawn();SavedView=PC->GetViewTarget();HeldObject=Object;FocusedObject.Reset();
 for(UPrimitiveComponent* Body:Components)
 {
  FBodyState State;State.Body=Body;State.Collision=Body->GetCollisionEnabled();
  State.bSimulating=Body->IsSimulatingPhysics();State.bGravity=Body->IsGravityEnabled();State.bAwake=Body->IsAnyRigidBodyAwake();
  State.Velocity=Body->GetPhysicsLinearVelocity();State.AngularVelocity=Body->GetPhysicsAngularVelocityInRadians();
  Bodies.Add(State);Body->SetSimulatePhysics(false);Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 }
 Object->DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
 PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);bLocksHeld=true;
 bSavedMouseCursor=PC->bShowMouseCursor;SavedCursor=uint8(PC->CurrentMouseCursor.GetValue());
 FInputModeGameAndUI Mode;Mode.SetHideCursorDuringCapture(false);Mode.SetLockMouseToViewportBehavior(EMouseLockMode::LockAlways);
 PC->SetInputMode(Mode);PC->bShowMouseCursor=true;PC->CurrentMouseCursor=EMouseCursor::GrabHand;
 if(ACharacter* Character=Cast<ACharacter>(SavedPawn.Get()))
 {
  auto* Movement=Character->GetCharacterMovement();SavedMovementMode=uint8(Movement->MovementMode);SavedCustomMode=Movement->CustomMovementMode;bMovementSaved=true;
  Character->StopJumping();Movement->StopMovementImmediately();Movement->DisableMovement();
 }
 TInlineComponentArray<UMeshComponent*> PlayerMeshes(SavedPawn.Get());
 for(UMeshComponent* Mesh:PlayerMeshes)if(!Mesh->bHiddenInGame){HiddenMeshes.Add(Mesh);Mesh->SetHiddenInGame(true);}
 Phase=EStationInspectionPhase::PickingUp;Elapsed=0;InputSuppressedFrame=GFrameCounter;
 PC->SetViewTargetWithBlend(InspectionCamera,FMath::Max(.1f,BlendSeconds),VTBlend_Cubic,0,true);
 if(Object->PickupSound)UGameplayStatics::PlaySound2D(this,Object->PickupSound,.65f);
 Object->OnInspectionStarted(PC);
 return true;
}

FTransform UStationInspectionComponent::HeldTransform() const
{
 const FVector Center=InspectionCamera->GetActorLocation()+InspectionCamera->GetActorForwardVector()*Distance;
 return FTransform(CurrentRotation,Center-CurrentRotation.RotateVector(LocalCenter*OriginalWorld.GetScale3D()),OriginalWorld.GetScale3D());
}

FTransform UStationInspectionComponent::ReturnTransform() const
{
 return SavedParent.IsValid()?OriginalRelative*SavedParent->GetSocketTransform(SavedSocket):OriginalWorld;
}

void UStationInspectionComponent::RotateObject(float Horizontal,float Vertical,float Roll)
{
 if(Phase!=EStationInspectionPhase::Inspecting || !InspectionCamera)return;
 const FQuat CameraRotation=InspectionCamera->GetActorQuat();
 const float Sensitivity=FMath::Clamp(RotationSensitivity,.05f,2.f);
 const FQuat Yaw(CameraRotation.GetUpVector(),FMath::DegreesToRadians(Horizontal*Sensitivity));
 const FQuat Pitch(CameraRotation.GetRightVector(),FMath::DegreesToRadians(-Vertical*Sensitivity));
 const FQuat Twist(CameraRotation.GetForwardVector(),FMath::DegreesToRadians(Roll*Sensitivity));
 TargetRotation=(Twist*Pitch*Yaw*TargetRotation).GetNormalized();
}

void UStationInspectionComponent::ZoomObject(float Steps)
{
 if(Phase==EStationInspectionPhase::Inspecting)
  TargetDistance=FMath::Clamp(TargetDistance*FMath::Pow(.88f,FMath::Clamp(Steps,-20.f,20.f)),MinimumDistance,MaximumDistance);
}

void UStationInspectionComponent::HandlePointerButton(bool bPressed)
{
 if(bPressed)
 {
  APlayerController* PC=Player();float X=0,Y=0;
  bPointerDragging=Phase==EStationInspectionPhase::Inspecting && PC && !PC->IsPaused() && PC->GetMousePosition(X,Y);
  LastPointerPosition=FVector2D(X,Y);
  if(bPointerDragging)PC->CurrentMouseCursor=EMouseCursor::GrabHandClosed;
 }
 else
 {
  UpdatePointerDrag();bPointerDragging=false;
  if(IsInspectingObject() && Player())Player()->CurrentMouseCursor=EMouseCursor::GrabHand;
 }
}

void UStationInspectionComponent::UpdatePointerDrag()
{
 APlayerController* PC=Player();float X=0,Y=0;
 if(!bPointerDragging || !PC || PC->IsPaused() || !PC->GetMousePosition(X,Y))return;
 const FVector2D Position(X,Y),Delta=Position-LastPointerPosition;
 LastPointerPosition=Position;
 RotateObject(Delta.X,-Delta.Y);
}

void UStationInspectionComponent::ResetPose()
{
 if(Phase==EStationInspectionPhase::Inspecting){TargetRotation=HomeRotation;TargetDistance=HomeDistance;}
}

void UStationInspectionComponent::ReturnObject()
{
 if(!IsInspectingObject() || Phase==EStationInspectionPhase::Returning)return;
 bPointerDragging=false;
 if(!HeldObject.IsValid()){CancelInspection();return;}
 ReturnStart=HeldObject->GetActorTransform();Phase=EStationInspectionPhase::Returning;Elapsed=0;
 if(APlayerController* PC=Player())
  if(AActor* View=SavedView.IsValid()?SavedView.Get():PC->GetPawn())PC->SetViewTargetWithBlend(View,FMath::Max(.1f,BlendSeconds),VTBlend_Cubic,0,true);
}

void UStationInspectionComponent::Finish(bool bPlaySound)
{
 if(!IsInspectingObject())return;
 APlayerController* PC=Player();
 AStationInspectable* Object=HeldObject.Get();
 if(Object)
 {
  Object->SetActorTransform(ReturnTransform(),false,nullptr,ETeleportType::TeleportPhysics);
  if(SavedParent.IsValid())
  {
   Object->AttachToComponent(SavedParent.Get(),FAttachmentTransformRules::KeepWorldTransform,SavedSocket);
   Object->GetRootComponent()->SetRelativeTransform(OriginalRelative,false,nullptr,ETeleportType::TeleportPhysics);
  }
 }
 for(const FBodyState& State:Bodies)if(UPrimitiveComponent* Body=State.Body.Get())
 {
  Body->SetCollisionEnabled(State.Collision);Body->SetEnableGravity(State.bGravity);Body->SetSimulatePhysics(State.bSimulating);
  if(State.bSimulating)
  {
   Body->SetPhysicsLinearVelocity(State.Velocity);Body->SetPhysicsAngularVelocityInRadians(State.AngularVelocity);
   if(!State.bAwake)Body->PutAllRigidBodiesToSleep();
  }
 }
 if(PC)
 {
  // Do not steal a view target assigned by a cinematic or another system.
  if(PC->GetViewTarget()==InspectionCamera || (Phase==EStationInspectionPhase::PickingUp && PC->GetViewTarget()==SavedView.Get()))
   if(AActor* View=SavedView.IsValid()?SavedView.Get():PC->GetPawn())PC->SetViewTarget(View);
  if(bLocksHeld){PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);}
  PC->bShowMouseCursor=bSavedMouseCursor;PC->CurrentMouseCursor=EMouseCursor::Type(SavedCursor);
  PC->SetInputMode(FInputModeGameOnly());
 }
 if(bMovementSaved)if(ACharacter* Character=Cast<ACharacter>(SavedPawn.Get()))
 {
  Character->StopJumping();Character->GetCharacterMovement()->SetMovementMode(EMovementMode(SavedMovementMode),SavedCustomMode);
 }
 for(auto& Mesh:HiddenMeshes)if(Mesh.IsValid())Mesh->SetHiddenInGame(false);
 if(InspectionCamera){InspectionCamera->Destroy();InspectionCamera=nullptr;}
 Bodies.Empty();HiddenMeshes.Empty();HeldObject.Reset();FocusedObject.Reset();SavedParent.Reset();SavedPawn.Reset();SavedView.Reset();
 bLocksHeld=false;bMovementSaved=false;bPointerDragging=false;Phase=EStationInspectionPhase::Idle;InputSuppressedFrame=GFrameCounter+1;
 if(Object)
 {
  if(bPlaySound && Object->ReturnSound)UGameplayStatics::PlaySoundAtLocation(this,Object->ReturnSound,Object->GetActorLocation(),.65f);
  Object->OnInspectionFinished(PC);
 }
}

void UStationInspectionComponent::CancelInspection(){Finish(false);}

void UStationInspectionComponent::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* Function)
{
 Super::TickComponent(Dt,TickType,Function);
 APlayerController* PC=Player();
 if(!PC || !PC->IsLocalController())return;
 if(!Overlay)CreateOverlay();
 if(!IsInspectingObject())
 {
  FocusedObject=FindFocusedObject();
  if(FocusedObject.IsValid() && (PC->WasInputKeyJustPressed(EKeys::E) || PC->WasInputKeyJustPressed(EKeys::LeftMouseButton)))BeginInspection(FocusedObject.Get());
  return;
 }
 if(!HeldObject.IsValid() || !SavedPawn.IsValid() || PC->GetPawn()!=SavedPawn.Get() || !InspectionCamera
  || (Phase==EStationInspectionPhase::Inspecting && PC->GetViewTarget()!=InspectionCamera))
 {CancelInspection();return;}
 if(PC->IsPaused())return;
 Elapsed+=Dt;
 const float Duration=FMath::Max(.1f,BlendSeconds);
 const float Alpha=FMath::Clamp(Elapsed/Duration,0.f,1.f);
 const float Smooth=Alpha*Alpha*(3.f-2.f*Alpha);
 if(Phase!=EStationInspectionPhase::Returning && GFrameCounter>InputSuppressedFrame
  && (PC->WasInputKeyJustPressed(EKeys::E) || PC->WasInputKeyJustPressed(EKeys::Escape) || PC->WasInputKeyJustPressed(EKeys::Tab)))
 {ReturnObject();return;}
 if(Phase==EStationInspectionPhase::PickingUp)
 {
  FTransform Pose;Pose.Blend(OriginalWorld,HeldTransform(),Smooth);HeldObject->SetActorTransform(Pose,false,nullptr,ETeleportType::TeleportPhysics);
  if(Alpha>=1.f)Phase=EStationInspectionPhase::Inspecting;
 }
 else if(Phase==EStationInspectionPhase::Returning)
 {
  FTransform Pose;Pose.Blend(ReturnStart,ReturnTransform(),Smooth);HeldObject->SetActorTransform(Pose,false,nullptr,ETeleportType::TeleportPhysics);
  if(Alpha>=1.f)Finish(true);
 }
 else
 {
  UpdatePointerDrag();
  if(bPointerDragging && !PC->IsInputKeyDown(EKeys::LeftMouseButton))HandlePointerButton(false);
  const float KeySpeed=180.f*Dt;
  RotateObject((float(PC->IsInputKeyDown(EKeys::Right))-float(PC->IsInputKeyDown(EKeys::Left)))*KeySpeed,
   (float(PC->IsInputKeyDown(EKeys::Up))-float(PC->IsInputKeyDown(EKeys::Down)))*KeySpeed,
   (float(PC->IsInputKeyDown(EKeys::X))-float(PC->IsInputKeyDown(EKeys::Z)))*KeySpeed);
  if(PC->WasInputKeyJustPressed(EKeys::MouseScrollUp))ZoomObject(1);
  if(PC->WasInputKeyJustPressed(EKeys::MouseScrollDown))ZoomObject(-1);
  if(PC->WasInputKeyJustPressed(EKeys::R))ResetPose();
  const float Response=1.f-FMath::Exp(-14.f*Dt);
  CurrentRotation=FQuat::Slerp(CurrentRotation,TargetRotation,Response).GetNormalized();
  Distance=FMath::Lerp(Distance,TargetDistance,Response);
  HeldObject->SetActorTransform(HeldTransform(),false,nullptr,ETeleportType::TeleportPhysics);
 }
}

FText UStationInspectionComponent::OverlayTitle() const
{
 const AStationInspectable* Object=IsInspectingObject()?HeldObject.Get():FocusedObject.Get();
 return Object?Object->DisplayName:FText::GetEmpty();
}

FText UStationInspectionComponent::OverlayDetail() const
{
 if(Phase==EStationInspectionPhase::PickingUp)return FText::FromString(TEXT("Lifting object..."));
 if(Phase==EStationInspectionPhase::Returning)return FText::FromString(TEXT("Returning to its original position..."));
 if(!IsInspectingObject())return FText::GetEmpty();
 const AStationInspectable* Object=HeldObject.Get();
 return Object?Object->Description:FText::GetEmpty();
}

FVector2D UStationInspectionComponent::FocusPromptPosition() const
{
 if(!FocusedObject.IsValid() || !Player())return FVector2D(-1000,-1000);
 FVector Center,Extent;FocusedObject->GetActorBounds(false,Center,Extent);
 FVector2D Screen;
 if(!Player()->ProjectWorldLocationToScreen(Center+FVector(0,0,Extent.Z+3.f),Screen,true))return FVector2D(-1000,-1000);
 int32 Width,Height;Player()->GetViewportSize(Width,Height);
 const FVector2D LocalSize=UWidgetLayoutLibrary::GetPlayerScreenWidgetGeometry(Player()).GetLocalSize();
 // Projected pixels may use a different render resolution from the Slate viewport.
 if(Width>0 && Height>0 && LocalSize.X>0 && LocalSize.Y>0)
  Screen=FVector2D(Screen.X*LocalSize.X/Width,Screen.Y*LocalSize.Y/Height);
 else Screen/=FMath::Max(.1f,UWidgetLayoutLibrary::GetViewportScale(Player()));
 return Screen-FVector2D(160,62);
}

void UStationInspectionComponent::CreateOverlay()
{
 if(!GEngine || !GEngine->GameViewport || !Player()->GetLocalPlayer())return;
 const TWeakObjectPtr<UStationInspectionComponent> WeakThis(this);
 const auto Active=[WeakThis]{return WeakThis.IsValid() && WeakThis->IsInspectingObject()?EVisibility::HitTestInvisible:EVisibility::Collapsed;};
 TSharedRef<SWidget> InspectionBar=SNew(SBox).VAlign(VAlign_Bottom).HAlign(HAlign_Fill).Padding(FMargin(32,0,32,32))
  .Visibility_Lambda(Active)
  [SNew(SVerticalBox)
     +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Justification(ETextJustify::Center).Font(FCoreStyle::GetDefaultFontStyle("Bold",18)).ColorAndOpacity(StationInteractionStyle::Action).ShadowOffset(FVector2D(1,1)).ShadowColorAndOpacity(InspectionShadow)
      .Text_Lambda([WeakThis]{return WeakThis.IsValid()?WeakThis->OverlayTitle():FText::GetEmpty();})]
     +SVerticalBox::Slot().AutoHeight().Padding(0,5,0,0)[SNew(STextBlock).Visibility_Lambda(Active).Justification(ETextJustify::Center).AutoWrapText(true).Font(FCoreStyle::GetDefaultFontStyle("Regular",12)).ColorAndOpacity(InspectionWhite).ShadowOffset(FVector2D(1,1)).ShadowColorAndOpacity(InspectionShadow)
      .Text_Lambda([WeakThis]{return WeakThis.IsValid()?WeakThis->OverlayDetail():FText::GetEmpty();})]
     +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Fill).Padding(0,10,0,0)
      [SNew(SWrapBox).UseAllottedSize(true).HAlign(HAlign_Center).InnerSlotPadding(FVector2D(20,8)).Visibility_Lambda(Active)
       +SWrapBox::Slot()[InspectionHint(SNew(SInspectionMouseIcon),TEXT("Drag to rotate"))]
       +SWrapBox::Slot()[InspectionHint(SNew(SInspectionMouseIcon).Wheel(true),TEXT("Scroll to zoom"))]
       +SWrapBox::Slot()[InspectionHint(InspectionKey(TEXT("Z / X")),TEXT("Roll"))]
       +SWrapBox::Slot()[InspectionHint(InspectionKey(TEXT("R")),TEXT("Reset"))]
       +SWrapBox::Slot()[InspectionHint(InspectionKey(TEXT("E / Esc / Tab")),TEXT("Return"))]]
  ];
 Overlay=SNew(SOverlay).Visibility(EVisibility::HitTestInvisible)
  +SOverlay::Slot()[InspectionBar]
  +SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
   [SNew(SBox).WidthOverride(6).HeightOverride(6)
    .Visibility_Lambda([WeakThis]{return WeakThis.IsValid() && WeakThis->CanSearch()?EVisibility::HitTestInvisible:EVisibility::Collapsed;})
    [SNew(SImage).Image(&AimDotBrush).ColorAndOpacity_Lambda([WeakThis]{return WeakThis.IsValid() && WeakThis->HasFocusedObject()?StationInteractionStyle::Action:InspectionWhite;})]]
  +SOverlay::Slot()
   [SNew(SCanvas).Visibility_Lambda([WeakThis]{return WeakThis.IsValid() && WeakThis->CanSearch() && WeakThis->FocusedObject.IsValid()?EVisibility::HitTestInvisible:EVisibility::Collapsed;})
    +SCanvas::Slot().Position_Lambda([WeakThis]{return WeakThis.IsValid()?WeakThis->FocusPromptPosition():FVector2D(-1000,-1000);}).Size(FVector2D(320,60))
     [SNew(SVerticalBox)
      +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Justification(ETextJustify::Center).Font(FCoreStyle::GetDefaultFontStyle("Bold",14)).ColorAndOpacity(StationInteractionStyle::Action).ShadowOffset(FVector2D(1,1)).ShadowColorAndOpacity(InspectionShadow)
       .Text_Lambda([WeakThis]{return WeakThis.IsValid()?WeakThis->OverlayTitle():FText::GetEmpty();})]
      +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,4,0,0)[InspectionHint(InspectionKey(TEXT("E / LMB")),TEXT("Examine"))]]];
 GEngine->GameViewport->AddViewportWidgetForPlayer(Player()->GetLocalPlayer(),Overlay.ToSharedRef(),20);
}

void UStationInspectionComponent::EndPlay(EEndPlayReason::Type Reason)
{
 CancelInspection();
 if(Overlay && GEngine && GEngine->GameViewport && Player() && Player()->GetLocalPlayer())
  GEngine->GameViewport->RemoveViewportWidgetForPlayer(Player()->GetLocalPlayer(),Overlay.ToSharedRef());
 Overlay.Reset();Super::EndPlay(Reason);
}
